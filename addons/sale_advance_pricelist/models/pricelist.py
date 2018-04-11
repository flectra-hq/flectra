# -*- coding: utf-8 -*-
# Part of flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models
from flectra.exceptions import UserError
from itertools import chain


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

    def get_product_price_rule_flectra(
            self, product, quantity, partner,
            rule_id, price_unit, date=False, uom_id=False):
        self.ensure_one()
        return self._compute_price_rule_flectra(
            [(product, quantity, partner)],
            rule_id, price_unit, date=date, uom_id=uom_id)[product.id]

    @api.multi
    def _compute_price_rule_flectra(self, products_qty_partner,
                                    rule_id, price_unit,
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
            'ORDER BY item.sequence,categ.parent_left desc',
            (prod_tmpl_ids, rule_id.ids, prod_ids,
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
                        if price != price_unit:
                            price = price_unit
                        if price < rule.discount_amount:
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
            if one_dis_price > 0.0:
                price = one_dis_price
            elif all_dis_price > 0.0:
                price = price - all_dis_price
            elif min_dis_price:
                price = price - min(min_dis_price)
            elif max_dis_price:
                price = price - max(max_dis_price)
            price = product.currency_id.compute(
                price, self.currency_id, round=False)
            results[product.id] = (price,
                                   suitable_rule and suitable_rule.id or False)
        return results
