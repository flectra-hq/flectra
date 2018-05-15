# -*- coding: utf-8 -*-
# Part of flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models
from flectra.exceptions import UserError
from itertools import chain
from flectra.tools import pycompat


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    pricelist_type = fields.Selection(
        [('basic', 'Basic'),
         ('advance', 'Advanced'),
         ], 'Pricelist Type', default='basic', required=True)
    apply_method = fields.Selection(
        [('first_matched_rule', 'Apply First Matched Rule'),
         ('all_matched_rules', 'Apply All Matched Rules'),
         ('smallest_discount', 'Apply Smallest Matched Discount'),
         ('biggest_discount', 'Apply Biggest Matched Discount')
         ], 'Apply Method', default='first_matched_rule', required=True)
    rule_ids = fields.One2many(
        'price.rule', 'pricelist_id', 'Price Rules',
        copy=True)
    cart_rule_ids = fields.One2many(
        'cart.rule', 'pricelist_id', 'Cart Rules Items',
        copy=True)
    apply_coupon_code = fields.Boolean('Apply Coupon Code?')
    coupon_code_lines = fields.One2many(
        'coupon.code', 'pricelist_id', 'Coupon Code Items',
        copy=True)

    def get_product_price_rule_advance(
            self, product, quantity, partner,
            date=False, uom_id=False):
        self.ensure_one()
        return self._compute_price_rule_advance(
            [(product, quantity, partner)],
            date=date, uom_id=uom_id)[product.id]

    @api.multi
    def _compute_price_rule_advance(self, products_qty_partner,
                                    date=False, uom_id=False):
        self.ensure_one()
        if not date:
            date = fields.Datetime.now()
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            products = [item[0].with_context(
                uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1],
                                     data_struct[2])
                                    for index, data_struct in
                                    enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = list(categ_ids)

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            prod_ids = [p.id for p in
                        list(chain.from_iterable(
                            [t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [
                product.product_tmpl_id.id for product in products]
        self._cr.execute(
            'SELECT item.id '
            'FROM rule_line AS item '
            'LEFT JOIN product_category AS categ '
            'ON item.categ_id = categ.id '
            'WHERE (item.product_tmpl_id IS NULL '
            'OR item.product_tmpl_id = any(%s))'
            'AND (item.price_rule_id = any(%s))'
            'AND (item.product_id IS NULL OR item.product_id = any(%s))'
            'AND (item.categ_id IS NULL OR item.categ_id = any(%s)) '
            'AND (item.pricelist_id = %s) '
            'AND (item.start_date IS NULL OR item.start_date<=%s) '
            'AND (item.end_date IS NULL OR item.end_date>=%s)'
            'ORDER BY item.sequence,item.id,categ.parent_left desc',
            (prod_tmpl_ids, self.rule_ids.ids, prod_ids,
             categ_ids, self.id, date, date))
        item_ids = [x[0] for x in self._cr.fetchall()]
        items = self.env['rule.line'].browse(item_ids)
        results = {}
        coupon_obj = self.env['coupon.code']
        partner_obj = self.env['res.partner']
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = \
                        self.env['product.uom'].browse(
                            [self._context['uom']])._compute_quantity(
                            qty, product.uom_id)
                except UserError:
                    pass
            price = product.price_compute('list_price')[product.id]
            one_dis_price = all_dis_price = 0.0
            max_dis_price = []
            min_dis_price = []
            partner_id = partner
            if isinstance(partner, int):
                partner_id = partner_obj.browse(partner)
            for rule in items:
                if rule.min_qty and qty_in_product_uom < rule.min_qty:
                    continue
                if rule.max_qty and qty_in_product_uom > rule.max_qty:
                    continue
                if rule.model_id:
                    check = coupon_obj.check_condition(rule, partner_id)
                    if check:
                        continue
                if is_product_template:
                    if rule.product_tmpl_id and \
                                    product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (
                                    product.product_variant_count == 1 and
                                    product.product_variant_id.id ==
                                    rule.product_id.id):
                        continue
                else:
                    if rule.product_tmpl_id and \
                                    product.product_tmpl_id.id != \
                                    rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue
                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue
                dis_price = 0.0
                if price is not False:
                    if rule.rule_type == 'fixed_amount':
                        price_unit = self._context.get('price_unit')
                        if price_unit and price != price_unit \
                                and self.discount_policy == 'without_discount':
                            price = price_unit
                        if price <= rule.discount_amount \
                                and self.apply_method != 'smallest_discount':
                            price = 0
                            suitable_rule = rule
                            break
                        else:
                            dis_price = price - rule.discount_amount
                    elif rule.rule_type == 'percent':
                        dis_price = (price - (price * (
                            rule.discount_amount / 100))) or 0.0
                    suitable_rule = rule
                if self.apply_method == 'first_matched_rule':
                    one_dis_price = dis_price
                    break
                elif self.apply_method == 'all_matched_rules':
                    all_dis_price += price - dis_price
                elif self.apply_method == 'smallest_discount':
                    min_dis_price.append(price - dis_price)
                else:
                    max_dis_price.append(price - dis_price)

            # Used context for add Cart Rules Discount
            cart_price = 0.0
            if self._context.get('order_id', False):
                order_id = self._context.get('order_id')
                cart_per = order_id.get_cart_rules_discount(
                    order_id.get_values())
                cart_price = price * (cart_per / 100) or 0.0
            if one_dis_price > 0.0:
                price = one_dis_price
            elif all_dis_price > 0.0:
                price = price - all_dis_price
            elif min_dis_price:
                price = price - min(min_dis_price)
            elif max_dis_price:
                price = price - max(max_dis_price)
            if cart_price > 0.0:
                price -= cart_price
            price = product.currency_id.compute(
                price, self.currency_id, round=False)
            results[product.id] = (price,
                                   suitable_rule and suitable_rule.id or False)
        return results

    # Used context for add Cart Rules Discount
    def get_products_price_advance(self, products, quantities,
                                   partners, date=False, uom_id=False):
        """ For a given pricelist, return price for products
        Returns: dict{product_id: product price}, in the given pricelist """
        self.ensure_one()
        vals = {
            product_id: res_tuple[0]
            for product_id, res_tuple in self._compute_price_rule_advance(
                list(pycompat.izip(products, quantities, partners)),
                date=date, uom_id=uom_id).items()
            }
        return vals


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Overrides Function
    # Used context for add Cart Rules Discount
    def _compute_product_price(self):
        prices = {}
        pricelist_id_or_name = self._context.get('pricelist')
        if pricelist_id_or_name:
            pricelist = None
            partner = self._context.get('partner', False)
            quantity = self._context.get('quantity', 1.0)
            if isinstance(pricelist_id_or_name, pycompat.string_types):
                pricelist_name_search = \
                    self.env['product.pricelist'].name_search(
                        pricelist_id_or_name, operator='=', limit=1)
                if pricelist_name_search:
                    pricelist = \
                        self.env['product.pricelist'].browse(
                            [pricelist_name_search[0][0]])
            elif isinstance(pricelist_id_or_name, pycompat.integer_types):
                pricelist = self.env['product.pricelist'].browse(
                    pricelist_id_or_name)

            if pricelist:
                quantities = [quantity] * len(self)
                partners = [partner] * len(self)
                if pricelist.pricelist_type == 'basic':
                    prices = pricelist.get_products_price(
                        self, quantities, partners)
                else:
                    prices = pricelist.with_context(
                        {'order_id': self._context.get('order_id')}
                    ).get_products_price_advance(
                        self, quantities, partners)
        for product in self:
            product.price = prices.get(product.id, 0.0)
            if self._context.get('order_id', False):
                return product.price
