# -*- coding: utf-8 -*-
# Part of flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.exceptions import Warning
from flectra.tools.safe_eval import safe_eval
from flectra.tools.misc import formatLang

MODELS_LIST = [
    'res.partner',
    'res.partner.category',
    'res.users',
    'res.groups',
    'res.country.state',
    'res.country',
]

Cart_Option = [
    ('subtotal_at_least', 'Subtotal At Least'),
    ('subtotal_less_than', 'Subtotal less than'),
    ('item_count_atleast', 'Lines Count at least'),
    ('item_count_less_than', 'Lines less than'),
    ('item_sum_qty_atleast', 'Sum of Item Qty at least'),
    ('item_sum_qty_less_than', 'Sum of Item Qty less than'),
    ('one_product_al_least', 'At least one product in order'),
    ('none_of_sel_products', 'None of selected Products'),
    ('one_categ_al_least', 'At least one category in order'),
    ('none_of_sel_categs', 'None of selected Categories'),
]


class RulesLine(models.Model):
    _name = 'rule.line'
    _order = 'sequence'

    sequence = fields.Integer('Sequence')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    min_qty = fields.Float('Min. Quantity')
    max_qty = fields.Float('Max. Quantity')
    rule_type = fields.Selection([
        ('percent', 'Percent'),
        ('fixed_amount', 'Fixed Amount'),
    ], 'Rule Type', required=True, default='percent')
    discount_amount = fields.Float('Discount Amount')
    price_rule_id = fields.Many2one('price.rule', 'Price Rule')
    model_id = fields.Many2one(
        'ir.model', string='Condition', domain=[('model', 'in', MODELS_LIST)])
    model_name = fields.Char(related='model_id.model', string='Model Name')
    model_domain = fields.Char(string='Domain', oldname='domain', default=[])
    model_real = fields.Char(compute='_compute_model', string='Real Model')
    pricelist_id = fields.Many2one(
        'product.pricelist',  related='price_rule_id.pricelist_id', store=True)
    categ_id = fields.Many2one(
        'product.category', related='price_rule_id.categ_id', store=True)
    product_tmpl_id = fields.Many2one(
        'product.template',
        related='price_rule_id.product_tmpl_id', store=True)
    product_id = fields.Many2one(
        'product.product', related='price_rule_id.product_id', store=True)
    rule_id_start_date = fields.Date(
        related='price_rule_id.start_date', store=True)
    rule_id_end_date = fields.Date(
        related='price_rule_id.end_date', store=True)

    @api.onchange('rule_type', 'discount_amount')
    def check_percentage(self):
        warning = {}
        if self.rule_type == 'percent' and (
                        self.discount_amount > 100 or
                        self.discount_amount < 0):
            warning.update({
                'title': _("Warning"),
                'message': _("Percentage should be between 0% to 100%!")})
            self.discount_amount = 0.0
            return {'warning': warning}

    @api.depends('model_id')
    def _compute_model(self):
        for record in self:
            if record.model_id:
                record.model_real = record.model_name or 'res.partner'

    @api.constrains('start_date', 'end_date',
                    'rule_id_start_date', 'rule_id_end_date')
    def check_date(self):
        for rule_line_id in self:
            parent_start_date = rule_line_id.rule_id_start_date
            child_start_date = rule_line_id.start_date
            if parent_start_date and \
                    child_start_date and parent_start_date > child_start_date:
                raise Warning(_("Start Date date not valid in "
                                "Product Rule Lines!"))
            parent_end_date = rule_line_id.rule_id_end_date
            child_end_date = rule_line_id.end_date
            if parent_end_date and \
                    child_end_date and parent_end_date < child_end_date:
                raise Warning(_("End Date date not valid in "
                                "Product Rule Lines!"))


class PriceRules(models.Model):
    _name = 'price.rule'
    _description = 'Price Rules'
    _order = 'sequence'

    @api.multi
    @api.depends('apply_on', 'categ_id', 'product_tmpl_id', 'product_id')
    def _get_pricerule_name_price(self):
        for record in self:
            if record.categ_id:
                record.name = _("Category: %s") % (record.categ_id.name)
            elif record.product_tmpl_id:
                record.name = record.product_tmpl_id.name
            elif record.product_id:
                record.name = record.product_id.display_name.replace(
                    '[%s]' % record.product_id.code, '')
            else:
                record.name = _("All Products")

    name = fields.Char('Name', compute='_get_pricerule_name_price')
    sequence = fields.Integer('Sequence')
    apply_on = fields.Selection([
        ('all', 'Global'),
        ('category', 'Category'),
        ('product_template', 'Product Template'),
        ('product', 'Product Variant')
    ], required=True, default='all', string="Apply On")
    categ_id = fields.Many2one('product.category', 'Category')
    product_tmpl_id = fields.Many2one('product.template', 'Product Template')
    product_id = fields.Many2one('product.product', 'Product')
    active = fields.Boolean('Active', default=True)
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    note = fields.Text('Description')
    pricelist_id = fields.Many2one('product.pricelist',
                                   'Pricelist', index=True, ondelete='cascade')
    rule_lines = fields.One2many('rule.line', 'price_rule_id',
                                 'Product Rule Lines')

    @api.onchange('apply_on')
    def _onchange_apply_on(self):
        if self.apply_on != 'product':
            self.product_id = False
        if self.apply_on != 'product_template':
            self.product_tmpl_id = False
        if self.apply_on != 'category':
            self.categ_id = False

    @api.multi
    def get_rules(self, pricelist_id, date):
        date = fields.Date.context_today(self)
        self._cr.execute(
            'SELECT rule.id '
            'FROM price_rule AS rule '
            'WHERE (rule.pricelist_id = %s) '
            'AND (rule.start_date IS NULL OR rule.start_date<=%s) '
            'AND (rule.end_date IS NULL OR rule.end_date>=%s)'
            'ORDER BY rule.sequence',
            (pricelist_id.id, date, date))
        rules_ids = [x[0] for x in self._cr.fetchall()]
        rules = self.browse(rules_ids)
        return rules


class CartRules(models.Model):
    _name = 'cart.rule'
    _description = 'Cart Rules'
    _order = 'sequence'

    @api.multi
    @api.depends('apply_on', 'amt_value', 'product_id', 'categ_id')
    def _get_cart_name_price(self):
        for record in self:
            select_option = dict(Cart_Option)
            if record.apply_on in ['subtotal_at_least', 'subtotal_less_than',
                                   'item_count_atleast',
                                   'item_count_less_than',
                                   'item_sum_qty_atleast',
                                   'item_sum_qty_less_than']:
                record.name = select_option[record.apply_on] + ' : ' + str(
                    formatLang(self.env, record.amt_value, digits=2))
            elif record.apply_on == 'one_product_al_least' and \
                    record.product_id:
                record.name = select_option[record.apply_on] + ' : ' + str(
                    record.product_id.name)
            elif record.apply_on == 'one_categ_al_least' and \
                    record.categ_id:
                record.name = select_option[record.apply_on] + ' : ' + str(
                    record.categ_id.name)
            elif record.apply_on:
                record.name = select_option[record.apply_on]

    name = fields.Char('Name', compute='_get_cart_name_price')
    sequence = fields.Integer('Sequence')
    active = fields.Boolean('Active', default=True)
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    discount_percentage = fields.Float('Discount (%)')
    apply_on = fields.Selection(Cart_Option, 'Apply On')
    amt_value = fields.Float('Amount')
    product_id = fields.Many2one('product.product', 'Product')
    product_ids = fields.Many2many('product.product', column1='cart_line_id',
                                   column2='product_id', string='Products')
    categ_id = fields.Many2one('product.category', 'Category')
    categ_ids = fields.Many2many('product.category', column1='cart_line_id',
                                 column2='category_id', string='Categories')
    note = fields.Text('Description')
    pricelist_id = fields.Many2one('product.pricelist')

    @api.onchange('discount_percentage')
    def check_percentage(self):
        warning = {}
        if self.discount_percentage > 100 or self.discount_percentage < 0:
            warning.update({
                'title': _("Warning"),
                'message': _("Percentage should be between 0% to 100%!")})
            self.discount_percentage = 0.0
            return {'warning': warning}

    def _get_cart_discount_amt(self, pricelist, total=0.0,
                               item_count=0.0, item_sum_count=0.0,
                               product_ids=[], categ_ids=[], order=False):
        discount_flag = False
        dis_price = 0.0
        if self.apply_on == 'subtotal_at_least' \
                and total >= self.amt_value:
            discount_flag = True
        elif self.apply_on == 'subtotal_less_than' and total <= self.amt_value:
            discount_flag = True
        elif self.apply_on == 'item_count_atleast' \
                and item_count >= self.amt_value:
            discount_flag = True
        elif self.apply_on == 'item_count_less_than' \
                and item_count <= self.amt_value:
            discount_flag = True
        elif self.apply_on == 'item_sum_qty_atleast' \
                and item_sum_count >= self.amt_value:
            discount_flag = True
        elif self.apply_on == 'item_sum_qty_less_than' \
                and item_sum_count <= self.amt_value:
            discount_flag = True
        elif self.apply_on == 'one_product_al_least' \
                and self.product_id.id in product_ids:
            discount_flag = True
        elif self.apply_on == 'none_of_sel_products' \
                and not any(map(lambda v: v in [
                    x.id for x in self.product_ids],
                                product_ids)):
            discount_flag = True
        elif self.apply_on == 'one_categ_al_least' \
                and self.categ_id.id in categ_ids:
            discount_flag = True
        elif self.apply_on == 'none_of_sel_categs' \
                and not any(map(lambda v: v in [
                    x.id for x in self.categ_ids], categ_ids)):
            discount_flag = True
        if discount_flag:
            dis_price = self.discount_percentage
        return dis_price


class CouponCode(models.Model):
    _name = 'coupon.code'
    _description = 'Coupon Code'

    @api.multi
    def _compute_order_count(self):
        sale_order_ids = self.env['sale.order'].search_count([
            ('coupon_code_id', '=', self.id), ('state', '=', 'sale')])
        self.sale_order_count = sale_order_ids
        self.remaining_limit = self.usage_limit - sale_order_ids

    name = fields.Char('Name')
    coupon_code = fields.Char('Coupon Code')
    code_valid_from = fields.Date('Valid From')
    code_valid_to = fields.Date('Valid To')
    sale_order_count = fields.Integer(
        compute='_compute_order_count', string='# of Sale Order')
    coupon_type = fields.Selection([
        ('percent', 'Percent'),
        ('fixed_amount', 'Fixed Amount'),
        ('buy_x_get_y', 'Buy X Product Get Y Product Free'),
        ('buy_x_get_y_other', 'Buy X Product Get Y Other Product Free'),
        ('buy_x_get_percent', 'Range Based Discount('
                              'Buy X Product Get Percent Free)'),
        ('clubbed', 'Clubbed Discount'),
    ], 'Coupon Type', default='percent', required=True)
    number_of_x_product = fields.Float('Number Of X Product')
    number_of_y_product = fields.Float('Number Of Y Product')
    other_categ_id = fields.Many2one('product.category', 'Category')
    discount_amount = fields.Float('Discount Amount')
    flat_discount = fields.Float('Flat Discount')
    extra_discount_percentage = fields.Float('Extra Discount')
    usage_limit = fields.Integer('Total Usage Limit')
    remaining_limit = fields.Integer(compute='_compute_order_count',
                                     string='Remaining Usage Limit')
    min_order_amount = fields.Float('Min Order Amount')
    active = fields.Boolean('Active', default=True)
    apply_on = fields.Selection([
        ('all', 'Global'),
        ('category', 'Category'),
        ('product_template', 'Product Template'),
        ('product', 'Product Variant'),
    ], required=True, default='all', string="Apply On")
    categ_id = fields.Many2one('product.category', 'Category')
    product_tmpl_id = fields.Many2one('product.template', 'Product Template')
    product_id = fields.Many2one('product.product', 'Product')
    other_product_id = fields.Many2one('product.product', 'Other Product')
    pricelist_id = fields.Many2one('product.pricelist',
                                   'Pricelist', index=True, ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Condition',
                               domain=[('model', 'in', MODELS_LIST)])
    model_name = fields.Char(related='model_id.model', string='Model Name')
    model_domain = fields.Char(string='Domain', oldname='domain', default=[])
    model_real = fields.Char(compute='_compute_model', string='Real Model')

    @api.onchange('apply_on')
    def _onchange_apply_on(self):
        if self.apply_on != 'product':
            self.product_id = False
        if self.apply_on != 'product_template':
            self.product_tmpl_id = False
        if self.apply_on != 'category':
            self.categ_id = False

    @api.onchange('coupon_type', 'discount_amount')
    def check_percentage(self):
        warning = {}
        if self.coupon_type == 'percent' and self.discount_amount > 100 \
                or self.discount_amount < 0:
            warning.update({
                'title': _("Warning"),
                'message': _("Percentage should be between 0% to 100%!")})
            self.discount_amount = 0.0
            return {'warning': warning}
        if self.coupon_type not in ['percent', 'fixed_amount',
                                    'buy_x_get_percent']:
            self.discount_amount = 0.0
        if self.coupon_type != 'clubbed':
            self.flat_discount = 0.0
            self.extra_discount_percentage = 0.0
        if self.coupon_type not in ['buy_x_get_y', 'buy_x_get_y_other',
                                    'buy_x_get_percent']:
            self.number_of_x_product = 0.0
            self.number_of_y_product = 0.0
            self.other_product_id = False

    @api.onchange('flat_discount', 'extra_discount_percentage')
    def check_clubbed_percentage(self):
        warning = {}
        percent = self.flat_discount + self.extra_discount_percentage
        if percent > 100 or percent < 0:
            warning.update({
                'title': _("Warning"),
                'message': _("Total Percentage ( Discount + Extra ) "
                             "should be between 0% to 100%!")})
            self.flat_discount = 0.0
            self.extra_discount_percentage = 0.0
            return {'warning': warning}

    @api.depends('model_id')
    def _compute_model(self):
        for record in self:
            if record.model_id:
                record.model_real = record.model_name or 'res.partner'

    @api.multi
    def view_sale_order(self):
        sale_order_ids = self.env['sale.order'].search([
            ('coupon_code_id', '=', self.id), ('state', '=', 'sale')])
        return {
            'name': 'Sales Orders',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form,kanban,pivot,graph',
            'res_model': 'sale.order',
            'domain': [('id', 'in', sale_order_ids.ids)],
        }

    @api.constrains('coupon_code')
    def check_duplicate_coupon_code(self):
        check_coupon_id = self.search([
            ('coupon_code', '=', self.coupon_code),
            ('id', '!=', self.id),
            ('pricelist_id', '=', self.pricelist_id.id)])
        if check_coupon_id:
            raise Warning(_("Coupon code (%s) already exists!") % (
                self.coupon_code))

    @api.multi
    def check_condition(self, record, partner_id):
        domain = safe_eval(record.model_domain)
        if record.model_real == 'res.partner':
            domain += [('id', '=', partner_id.id)]
        elif record.model_real == 'res.partner.category':
            domain += [('id', 'in', partner_id.category_id.ids)]
        elif record.model_real == 'res.users':
            domain += [('id', 'in', self.env.user.id)]
        elif record.model_real == 'res.groups':
            domain += [('users', 'in', self.env.user.id)]
        elif record.model_real == 'res.country.state':
            domain += [('id', '=', partner_id.state_id.id)]
        elif record.model_real == 'res.country':
            domain += [('id', '=', partner_id.country_id.id)]
        if self.env[record.model_real].search(domain):
            return False
        return True

    @api.multi
    def get_coupon_records(self, coupon_code, pricelist_id):
        coupon_ids = []
        if coupon_code:
            date = fields.Date.context_today(self)
            self._cr.execute(
                'SELECT code.id '
                'FROM coupon_code AS code '
                'WHERE (code.coupon_code = %s) '
                'AND (code.code_valid_from IS NULL OR '
                'code.code_valid_from<=%s) '
                'AND (code.code_valid_to IS NULL OR code.code_valid_to>=%s) '
                'AND (code.pricelist_id = %s) ',
                (coupon_code, date, date, pricelist_id.id))
            coupons = [x[0] for x in self._cr.fetchall()]
            coupon_ids = self.env['coupon.code'].browse(coupons)
        return coupon_ids

    @api.multi
    def get_coupon_discount(self, line, cal_coupon):
        if not line.order_id.pricelist_id.apply_coupon_code or not \
                line.coupon_code_id:
            return 0.0
        coupon_amount = 0.0
        onchange_context = True
        coupon_ids = self.get_coupon_records(line.order_id.have_coupon_code,
                                             line.order_id.pricelist_id)
        for coupon_id in coupon_ids:
            if coupon_id.coupon_type == 'percent' or \
                            coupon_id.coupon_type == 'clubbed':
                discount_per = coupon_id.discount_amount
                if coupon_id.coupon_type == 'clubbed':
                    discount_per = \
                        coupon_id.flat_discount + \
                        coupon_id.extra_discount_percentage
                coupon_amount += line.order_id._get_percentage_coupon_discount(
                    line, coupon_id, onchange_context,
                    cal_coupon, discount_per, False)
            elif coupon_id.coupon_type == 'fixed_amount':
                coupon_amount += line.order_id._get_fixed_coupon_discount(
                    line, coupon_id, onchange_context, cal_coupon, False)
            elif coupon_id.coupon_type == 'buy_x_get_percent' \
                    and line.product_uom_qty >= coupon_id.number_of_x_product:
                coupon_amount += \
                    line.order_id.buy_x_get_percentage_coupon_discount(
                        line, coupon_id, onchange_context, cal_coupon, False)
        return coupon_amount
