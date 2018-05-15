# -*- coding: utf-8 -*-
# Part of flectra. See LICENSE file for full copyright and licensing details.

import json

import flectra.addons.decimal_precision as dp
from flectra import api, fields, models, _
from flectra.exceptions import Warning, UserError
from flectra.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('amount_total', 'currency_id')
    def _get_amount_word(self):
        for order in self:
            if not order.currency_id:
                return
            order.amount_words = order.currency_id.amount_to_text(
                order.discount)

    @api.depends('order_line', 'partner_id', 'coupon_flag')
    def _check_cart_rules(self):
        for order in self:
            if order.pricelist_id.pricelist_type == 'advance':
                order._update_all()
                if order.pricelist_id.discount_policy == 'without_discount':
                    cart_discount = 0.0
                    cart_discount_per = \
                        order.get_cart_rules_discount(order.get_values())
                    for line in order.order_line:
                        if line.get_line_percentage() < 100:
                            cart_discount += \
                                ((line.price_unit * line.product_uom_qty
                                  ) * cart_discount_per) / 100
                    order.cart_discount = cart_discount
                else:
                    for line in order.order_line:
                        line.set_line_amount()

    @api.multi
    def get_cart_discount(self, cart_rule_id, values):
        cart_discount = cart_rule_id._get_cart_discount_amt(
            self.pricelist_id, total=values.get('amount_untaxed'),
            item_count=values.get('item_count'),
            item_sum_count=values.get('item_sum_count'),
            product_ids=values.get('product_ids'),
            categ_ids=values.get('categ_ids'), order=self)
        return cart_discount

    @api.multi
    def get_cart_rules_discount(self, values):
        if not self.pricelist_id:
            return 0.0
        date = fields.Date.context_today(self)
        self._cr.execute(
            'SELECT rule.id '
            'FROM cart_rule AS rule '
            'WHERE (rule.pricelist_id = %s) '
            'AND (rule.start_date IS NULL OR rule.start_date<=%s) '
            'AND (rule.end_date IS NULL OR rule.end_date>=%s)'
            'ORDER BY rule.sequence',
            (self.pricelist_id.id, date, date))
        item_ids = [x[0] for x in self._cr.fetchall()]
        cart_rule_ids = self.env['cart.rule'].browse(item_ids)
        if not cart_rule_ids:
            return 0.0
        final_dis_price = 0.0
        one_dis_price = all_dis_price = 0.0
        max_dis_price = []
        min_dis_price = []
        cart_discount = 0.0
        for cart_rule_id in cart_rule_ids:
            cart_discount = self.get_cart_discount(cart_rule_id, values)
            if cart_rule_id.pricelist_id.apply_method == \
                    'first_matched_rule' and \
                    cart_discount > 0.0:
                one_dis_price = cart_discount
                break
            elif cart_rule_id.pricelist_id.apply_method == 'all_matched_rules':
                all_dis_price += cart_discount
            elif cart_rule_id.pricelist_id.apply_method == \
                    'smallest_discount' and cart_discount:
                min_dis_price.append(cart_discount)
            else:
                max_dis_price.append(cart_discount)
        if one_dis_price > 0.0:
            final_dis_price = one_dis_price
        elif all_dis_price > 0.0:
            final_dis_price = all_dis_price
        elif min_dis_price:
            final_dis_price = min(min_dis_price)
        elif max_dis_price:
            final_dis_price = max(max_dis_price)
        return final_dis_price

    @api.model
    def _get_discount_vals(self):
        payment_vals = []
        price_list_discount = price_rule_discount = coupon_code_discount = 0.0
        coupon_code_obj = self.env['coupon.code']
        partner_id = self.partner_id
        pricelist_id = self.pricelist_id
        for line in self.order_line:
            if not (line.product_id and line.product_uom and
                    partner_id and pricelist_id and
                    pricelist_id.discount_policy == 'without_discount' and
                    self.env.user.has_group(
                        'sale.group_discount_per_so_line')):
                return
            if pricelist_id.pricelist_type == 'basic':
                price_list_discount = self.discount
            else:
                if line.product_uom_qty < 0 and line.coupon_code_id:
                    continue
                if line.order_id.have_coupon_code and line.coupon_code_id:
                    coupon_code_discount += \
                        coupon_code_obj.get_coupon_discount(line, True)
                if line.coupon_code_id and line.price_unit == 0:
                    continue
        if pricelist_id.pricelist_type != 'basic':
            price_rule_discount = (self.discount - coupon_code_discount
                                   ) - self.cart_discount
        untaxed_amount = self.gross_amount - self.discount
        payment_vals.append({
            'gross_amount': formatLang(self.env, self.gross_amount, digits=2),
            'price_list_discount':
                formatLang(self.env, price_list_discount, digits=2),
            'price_rule_discount':
                formatLang(self.env, price_rule_discount, digits=2),
            'cart_rule_discount':
                formatLang(self.env, self.cart_discount, digits=2),
            'coupon_code_discount':
                formatLang(self.env, coupon_code_discount, digits=2),
            'currency': self.pricelist_id.currency_id.symbol,
            'untaxed_amount': formatLang(self.env, untaxed_amount, digits=2),
            'position': self.pricelist_id.currency_id.position,
            'amount_words': self.amount_words,
            'discount': formatLang(self.env, self.discount, digits=2),
        })
        return payment_vals

    @api.depends('discount')
    def _get_discount_info_JSON(self):
        for record in self:
            info = {'title': _('Discount'), 'outstanding': False,
                    'content': record._get_discount_vals()}
            record.discount_widget = json.dumps(info)

    def _update_all(self):
        for order in self:
            amount_untaxed = amount_tax = item_count = item_sum_count = 0.0
            product_ids = categ_ids = []
            check_dup_product = []
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                item_sum_count += line.product_uom_qty
                if line.product_id.id not in check_dup_product:
                    item_count += 1
                    check_dup_product.append(line.product_id.id)
                product_ids.append(line.product_id.id)
                categ_ids.append(line.product_id.categ_id.id)
            return {
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'item_sum_count': item_sum_count,
                'item_count': item_count,
                'product_ids': product_ids,
                'categ_ids': categ_ids,
            }

    @api.multi
    def get_values(self):
        return self._update_all()

    have_coupon_code = fields.Char('Have Coupon Code')
    cart_discount = fields.Float(
        compute='_check_cart_rules', string='Cart Discount')
    coupon_flag = fields.Boolean('Check Coupon Apply')
    amount_words = fields.Char(string="Discount Amount Words",
                               compute='_get_amount_word', store=True)
    discount_widget = fields.Text(compute='_get_discount_info_JSON')
    coupon_code_id = fields.Many2one('coupon.code', 'Coupon Ref')

    @api.multi
    def _get_percentage_coupon_discount(self, line, coupon_code_id,
                                        onchange_context, cal_coupon,
                                        discount_per, remove):
        coupon_discount_amount = 0.0
        total_price = (line.product_uom_qty * line.price_unit)
        if self.coupon_flag and not onchange_context and line.coupon_code_id:
            if line.dummy_discount:
                percent = line.dummy_discount - discount_per
            else:
                percent = line.discount - discount_per
            line.write({'check_coupon': False,
                        'discount': percent,
                        'coupon_code_id': False,
                        'check_coupon': False})
        elif not cal_coupon and not remove:
            coupon_discount_amount = (total_price * discount_per) / 100
            percent = line.discount + discount_per
            if percent > 100:
                line.dummy_discount = percent
                line.discount = 100
            else:
                line.discount = percent
                line.dummy_discount = 0.0
            line.coupon_code_id = coupon_code_id.id
            line.check_coupon = True
        else:
            coupon_discount_amount = (total_price * discount_per) / 100
        return coupon_discount_amount

    @api.multi
    def _get_fixed_coupon_discount(self, line, coupon_code_id,
                                   onchange_context, cal_coupon, remove):
        line_discount = 0.0
        if not line.price_unit:
            return 0.0
        discount_amount = 0.0
        if line.price_unit < coupon_code_id.discount_amount:
            discount_amount = line.price_unit
        if self.coupon_flag and not onchange_context and line.coupon_code_id:
            if discount_amount:
                line_discount = (line.price_unit * line.dummy_discount / 100
                                 ) - line.price_unit
                line.write({'check_coupon': False,
                            'discount': line_discount / line.price_unit * 100,
                            'coupon_code_id': False})
            else:
                if line.dummy_discount:
                    line_discount = \
                        (line.price_unit * line.dummy_discount / 100
                         ) - coupon_code_id.discount_amount
                else:
                    line_discount = (line.price_unit * line.discount / 100
                                     ) - coupon_code_id.discount_amount
                line.write({'check_coupon': False,
                            'discount': line_discount / line.price_unit * 100,
                            'coupon_code_id': False})
        elif not cal_coupon and not remove:
            if discount_amount:
                line_discount = (line.price_unit * line.discount / 100
                                 ) + discount_amount
            else:
                line_discount = (line.price_unit * line.discount / 100
                                 ) + coupon_code_id.discount_amount
            percent = line_discount / line.price_unit * 100
            if percent > 100:
                line.dummy_discount = percent
                line.discount = 100
            else:
                line.discount = percent
            line.coupon_code_id = coupon_code_id.id
            line.check_coupon = True
        return line.product_uom_qty * coupon_code_id.discount_amount

    @api.multi
    def _get_same_product_coupon_discount(self, line, coupon_code_id, remove):
        qty = int((line.product_uom_qty / coupon_code_id.number_of_x_product)
                  ) * coupon_code_id.number_of_y_product
        if line.coupon_code_id and line.check_coupon:
            line.write({'check_coupon': False, 'coupon_code_id': False})
        elif self.coupon_flag and line.coupon_code_id and \
                not line.check_coupon:
            line.unlink()
        elif line.product_uom_qty == coupon_code_id.number_of_x_product and \
                not remove:
            line.write({'check_coupon': True,
                        'coupon_code_id': coupon_code_id.id})
            self.env['sale.order.line'].create(
                {
                    'product_id': line.product_id.id,
                    'product_uom_qty': coupon_code_id.number_of_y_product,
                    'order_id': self.id,
                    'discount': 0.0,
                    'coupon_code_id': coupon_code_id.id,
                    'price_unit': 0.0
                })
        elif not self.coupon_flag and qty >= 1:
            line.write({'check_coupon': True,
                        'coupon_code_id': coupon_code_id.id})
            self.env['sale.order.line'].create(
                {
                    'product_id': line.product_id.id,
                    'product_uom_qty': int(qty),
                    'order_id': self.id,
                    'discount': 0.0,
                    'coupon_code_id': coupon_code_id.id,
                    'price_unit': 0.0
                })

    @api.multi
    def _get_other_product_coupon_discount(self, line, coupon_code_id):
        qty = int((line.product_uom_qty / coupon_code_id.number_of_x_product)
                  ) * coupon_code_id.number_of_y_product
        if line.coupon_code_id and line.check_coupon:
            line.write({'check_coupon': False, 'coupon_code_id': False})
            return 0.0
        elif self.coupon_flag and line.coupon_code_id \
                and not line.check_coupon:
            line.unlink()
            return 0.0
        elif not self.coupon_flag and qty >= 1:
            line.write({'check_coupon': True,
                        'coupon_code_id': coupon_code_id.id})
            return qty
        return 0.0

    @api.multi
    def buy_x_get_percentage_coupon_discount(
            self, line, coupon_code_id, onchange_context, cal_coupon, remove):
        coupon_discount_amount = 0.0
        total_price = (line.product_uom_qty * line.price_unit)
        if self.coupon_flag and not onchange_context and line.coupon_code_id \
                and line.product_uom_qty >= coupon_code_id.number_of_x_product:
            if line.dummy_discount:
                percent = line.dummy_discount - coupon_code_id.discount_amount
            else:
                percent = line.discount - coupon_code_id.discount_amount
            line.write({'check_coupon': False,
                        'discount': percent,
                        'coupon_code_id': False,
                        'check_coupon': False})
        elif not cal_coupon and not remove and line.product_uom_qty >= \
                coupon_code_id.number_of_x_product:
            coupon_discount_amount = \
                (total_price * coupon_code_id.discount_amount) / 100
            percent = line.discount + coupon_code_id.discount_amount
            if percent > 100:
                line.dummy_discount = percent
                line.discount = 100
            else:
                line.discount = percent
                line.dummy_discount = 0.0
            line.coupon_code_id = coupon_code_id.id
            line.check_coupon = True
        else:
            coupon_discount_amount = \
                (total_price * coupon_code_id.discount_amount) / 100
        return coupon_discount_amount

    @api.multi
    def _check_Constraints(self):
        self.get_values()
        order_line = self.order_line
        if not self.have_coupon_code:
            raise UserError(_("Please enter the Coupon code!"))
        if not order_line:
            raise UserError(_("There is no sale order line!"))
        if self.pricelist_id.pricelist_type != 'advance' or not \
                self.pricelist_id.apply_coupon_code:
            raise UserError(_("Coupon code does not apply to "
                              "sale order pricelist!"))
        coupon_obj = self.env['coupon.code']
        coupon_code_id = coupon_obj.get_coupon_records(
            self.have_coupon_code, self.pricelist_id)
        if not coupon_code_id:
            raise UserError(_("Coupon code (%s) not found!"
                              ) % (self.have_coupon_code))
        if coupon_code_id.usage_limit > 0 \
                and coupon_code_id.remaining_limit <= 0:
            raise UserError(_("Coupon code (%s) Remaining Limit exceeds!"
                              ) % (self.have_coupon_code))
        if coupon_code_id.min_order_amount \
                and self.amount_untaxed < coupon_code_id.min_order_amount \
                and not self.env.context.get('remove', False):
            raise UserError(_("Untaxed Amount (%s) must be greater than "
                              "Min Order Amount (%s) which required for "
                              "the apply coupon code!") % (
                formatLang(self.env, self.amount_untaxed, digits=2),
                formatLang(self.env, coupon_code_id.min_order_amount,
                           digits=2)))
        if coupon_code_id.model_id:
            check_coupon = coupon_obj.check_condition(
                coupon_code_id, self.partner_id)
            if check_coupon:
                raise Warning(_("Coupon code (%s) condition criteria not "
                                "match!") % (self.have_coupon_code))
        return coupon_code_id

    @api.multi
    def apply_coupon_code(self):
        if self._context.get('website_id', False):
            coupon_obj = self.env['coupon.code']
            coupon_id = coupon_obj.get_coupon_records(
                self.have_coupon_code, self.pricelist_id)
        else:
            coupon_id = self._check_Constraints()
        order_line = self.order_line
        coupon_discount_amount = 0.0
        have_coupon_code = self.have_coupon_code
        coupon_flag = True
        onchange_context = True
        coupon_ref_id = coupon_id.id
        remove = False
        cal_coupon = False
        if self.coupon_flag:
            have_coupon_code = ''
            coupon_flag = False
            onchange_context = False
            coupon_ref_id = False
            remove = True
        check_coupon = True
        qty = 0.0
        for line in order_line:
            if coupon_id.apply_on == 'category' and not \
                            line.product_id.categ_id == coupon_id.categ_id:
                continue
            elif coupon_id.apply_on == 'product_template' and not \
                    line.product_id.product_tmpl_id == \
                    coupon_id.product_tmpl_id:
                continue
            elif coupon_id.apply_on == 'product' and not \
                    line.product_id == coupon_id.product_id:
                continue
            else:
                if coupon_id.coupon_type == 'percent' or \
                                coupon_id.coupon_type == 'clubbed':
                    discount_per = coupon_id.discount_amount
                    if coupon_id.coupon_type == 'clubbed':
                        discount_per = coupon_id.flat_discount + \
                                       coupon_id.extra_discount_percentage
                    coupon_discount_amount += \
                        self._get_percentage_coupon_discount(
                            line, coupon_id, onchange_context,
                            cal_coupon, discount_per, remove)
                    check_coupon = False
                elif coupon_id.coupon_type == 'fixed_amount':
                    coupon_discount_amount += self._get_fixed_coupon_discount(
                        line, coupon_id, onchange_context, cal_coupon, remove)
                    check_coupon = False
                elif coupon_id.coupon_type == 'buy_x_get_y' and \
                        coupon_id.number_of_x_product and \
                        coupon_id.number_of_y_product:
                    if line.product_uom_qty < \
                        coupon_id.number_of_x_product and not \
                            line.coupon_code_id and check_coupon:
                        check_coupon = True
                        continue
                    self._get_same_product_coupon_discount(
                        line, coupon_id, remove)
                    check_coupon = False
                elif coupon_id.coupon_type == 'buy_x_get_y_other':
                    if line.product_uom_qty < \
                            coupon_id.number_of_x_product and not \
                            line.coupon_code_id and check_coupon:
                        check_coupon = True
                        continue
                    qty += self._get_other_product_coupon_discount(
                        line, coupon_id)
                    check_coupon = False
                elif coupon_id.coupon_type == 'buy_x_get_percent':
                    if line.product_uom_qty < \
                            coupon_id.number_of_x_product and not \
                            line.coupon_code_id and check_coupon:
                        check_coupon = True
                        continue
                    coupon_discount_amount += \
                        self.buy_x_get_percentage_coupon_discount(
                            line, coupon_id, onchange_context,
                            cal_coupon, remove)
                    check_coupon = False
        if check_coupon and not self._context.get('website_id', False):
            raise Warning(_("Coupon code (%s) condition criteria not match!"
                            ) % (self.have_coupon_code))
        if qty:
            self.env['sale.order.line'].create({
                'product_id': coupon_id.other_product_id.id,
                'product_uom_qty': int(qty), 'order_id': self.id,
                'coupon_code_id': coupon_id.id, 'price_unit': 0.0})
        self.write({'have_coupon_code': have_coupon_code,
                    'coupon_flag': coupon_flag,
                    'coupon_code_id': coupon_ref_id})


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    coupon_code_id = fields.Many2one('coupon.code', 'Coupon Ref')
    check_coupon = fields.Boolean('Apply Coupon')
    dummy_discount = fields.Float(
        string='Discount (%)',
        digits=dp.get_precision('Discount'), default=0.0)

    @api.multi
    def get_line_percentage(self):
        self._onchange_discount()
        discount = self.discount
        if discount > 100:
            self.dummy_discount = discount
            discount = 100
        self.discount = discount
        return discount

    @api.multi
    def set_line_amount(self):
        discount, product_price = self.get_rule_discount()
        if product_price:
            discount = product_price * (discount) / 100
        self.price_unit = product_price - discount

    @api.multi
    def get_total_coupon_code(self):
        return self.env['coupon.code'].get_coupon_discount(self, False)

    def _get_real_price_currency_advance(self, product, uom,
                                         pricelist_id, price_unit):
        currency_id = pricelist_id.currency_id
        product_currency = \
            (product.company_id and product.company_id.currency_id
             ) or self.env.user.company_id.currency_id
        if currency_id.id == product_currency.id:
            cur_factor = 1.0
        else:
            cur_factor = currency_id._get_conversion_rate(
                product_currency, currency_id)
        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0
        return price_unit * uom_factor * cur_factor, currency_id.id

    @api.multi
    def get_rule_discount(self):
        date = fields.Date.context_today(self)
        rules = self.env['price.rule'].get_rules(
            self.order_id.pricelist_id, date)
        max_dis_price = []
        min_dis_price = []
        discount_per = 0.0
        apply_method = self.order_id.pricelist_id.apply_method
        discount = 0.0
        context_partner = dict(self.env.context,
                               partner_id=self.order_id.partner_id.id,
                               date=self.order_id.date_order)
        pricelist_context = dict(context_partner, uom=self.product_uom.id,
                                 order_id=self.order_id,
                                 price_unit=self.price_unit)
        product_price = 0.0
        for rule in rules:
            adv_price, adv_rule_id = \
                self.order_id.pricelist_id.with_context(
                    pricelist_context).get_product_price_rule_advance(
                    self.product_id, self.product_uom_qty,
                    self.order_id.partner_id)
            rule_line_id = self.env['rule.line'].browse(adv_rule_id)
            adv_new_price = 0.0
            currency_id = False
            if not rule_line_id:
                adv_new_price, currency_id = self.with_context(
                    context_partner)._get_real_price_currency(
                    self.product_id, False,
                    self.product_uom_qty,
                    self.product_uom,
                    self.order_id.pricelist_id.id)
            else:
                if rule_line_id.rule_type == 'percent':
                    adv_new_price, currency_id = self.with_context(
                        context_partner)._get_real_price_currency(
                        self.product_id, False,
                        self.product_uom_qty,
                        self.product_uom,
                        self.order_id.pricelist_id.id)
                elif rule_line_id.rule_type == 'fixed_amount':
                    adv_new_price, currency_id = self.with_context(
                        context_partner)._get_real_price_currency_advance(
                        self.product_id,
                        self.product_uom,
                        self.order_id.pricelist_id, self.price_unit)
            if adv_new_price != 0:
                if self.order_id.pricelist_id.currency_id.id != currency_id:
                    adv_new_price = self.env['res.currency'].browse(
                        currency_id).with_context(context_partner).compute(
                        adv_new_price, rule.pricelist_id.currency_id)
                if not product_price:
                    product_price = adv_new_price
                discount_per =\
                    (adv_new_price - adv_price) / adv_new_price * 100
                if apply_method == 'first_matched_rule':
                    discount += discount_per
                    break
                elif apply_method == 'all_matched_rules':
                    discount += discount_per
                elif apply_method == 'smallest_discount' and adv_rule_id:
                    min_dis_price.append(discount_per)
                else:
                    max_dis_price.append(discount_per)
        if min_dis_price:
            discount += min(min_dis_price)
        if max_dis_price:
            discount += max(max_dis_price)
        return discount, product_price

    # Overrides Function
    @api.onchange('product_id', 'price_unit', 'product_uom',
                  'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        self.discount = 0.0
        if not (self.product_id and self.product_uom and
                self.order_id.partner_id and self.order_id.pricelist_id and
                self.order_id.pricelist_id.discount_policy ==
                'without_discount' and
                self.env.user.has_group('sale.group_discount_per_so_line')):
            return
        discount = 0.0
        context_partner = dict(self.env.context,
                               partner_id=self.order_id.partner_id.id,
                               date=self.order_id.date_order)
        pricelist_context = dict(context_partner, uom=self.product_uom.id)
        if self.order_id.pricelist_id.pricelist_type == 'basic':
            price, rule_id = self.order_id.pricelist_id.with_context(
                pricelist_context).get_product_price_rule(
                self.product_id, self.product_uom_qty or 1.0,
                self.order_id.partner_id)
            new_list_price, currency_id = self.with_context(
                context_partner)._get_real_price_currency(
                self.product_id, rule_id, self.product_uom_qty,
                self.product_uom, self.order_id.pricelist_id.id)
            if new_list_price != 0:
                if self.order_id.pricelist_id.currency_id.id != currency_id:
                    new_list_price = self.env['res.currency'].browse(
                        currency_id).with_context(context_partner).compute(
                        new_list_price, self.order_id.pricelist_id.currency_id)
                discount = (new_list_price - price) / new_list_price * 100
                if discount > 0:
                    self.discount = discount
        else:
            if self.coupon_code_id and (self._context.get(
                    'quantity', False) or self._context.get(
                    'price_unit', False) or self._context.get('tax', False)):
                raise Warning(_('You can not change order line. '
                                'Please remove coupon code first!'))
            discount, product_price = self.get_rule_discount()
            if discount > 0:
                self.discount = discount
            if self.order_id.have_coupon_code and self.coupon_code_id:
                self.get_total_coupon_code()
