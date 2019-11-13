# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.tools.misc import formatLang
from flectra.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    @api.depends('discount_amount', 'discount_per',
                 'amount_untaxed', 'order_line')
    def _get_discount(self):
        total_discount = 0.0
        for record in self:
            for so_line_id in record.order_line:
                total_price = \
                    (so_line_id.product_uom_qty * so_line_id.price_unit)
                total_discount += (total_price * so_line_id.discount) / 100
        record.discount = record.pricelist_id.currency_id.round(total_discount)

    @api.multi
    @api.depends('order_line', 'discount_per', 'discount_amount',
                 'order_line.product_uom_qty', 'order_line.price_unit')
    def _get_total_amount(self):
        for order_id in self:
            order_id.gross_amount = sum(
                [order_id.pricelist_id.currency_id.round(line_id.product_uom_qty *
                 line_id.price_unit) for line_id in order_id.order_line])

    discount_method = fields.Selection(
        [('fixed', 'Fixed'), ('per', 'Percentage')], string="Discount Method")
    discount_amount = fields.Float(string="Discount Amount")
    discount_per = fields.Float(string="Discount (%)")
    discount = fields.Monetary(
        string='Discount', store=True, readonly=True, compute='_get_discount',
        track_visibility='always')
    gross_amount = fields.Float(string="Gross Amount",
                                compute='_get_total_amount', store=True)

    @api.multi
    def calculate_discount(self):
        self._check_constrains()
        for line in self.order_line:
            line.write({'discount': 0.0})
        # amount_untaxed = self.amount_untaxed
        gross_amount = self.gross_amount
        if self.discount_method == 'per':
            for line in self.order_line:
                line.write({'discount': self.discount_per})
        else:
            for line in self.order_line:
                discount_value_ratio = \
                    (self.discount_amount *
                     line.price_subtotal) / gross_amount
                if discount_value_ratio:
                    discount_per_ratio = \
                        (discount_value_ratio * 100) / line.price_subtotal
                    line.write({'discount': discount_per_ratio})

    @api.onchange('discount_method')
    def onchange_discount_method(self):
        self.discount_amount = 0.0
        self.discount_per = 0.0
        if self.discount_method and not self.order_line:
            raise Warning('No Sale Order Line(s) were found!')

    @api.constrains('discount_per', 'discount_amount', 'order_line')
    def _check_constrains(self):
        self.onchange_discount_per()
        self.onchange_discount_amount()

    @api.multi
    def get_maximum_per_amount(self):
        sale_dis_config_obj = self.env['sale.discount.config']
        max_percentage = 0
        max_amount = 0
        check_group = False
        for groups_id in self.env.user.groups_id:
            sale_dis_config_id = \
                sale_dis_config_obj.search([('group_id', '=', groups_id.id)])
            if sale_dis_config_id:
                check_group = True
                if sale_dis_config_id.percentage > max_percentage:
                    max_percentage = sale_dis_config_id.percentage
                if sale_dis_config_id.fix_amount > max_amount:
                    max_amount = sale_dis_config_id.fix_amount
        return {'max_percentage': max_percentage,
                'max_amount': max_amount, 'check_group': check_group}

    @api.onchange('discount_per')
    def onchange_discount_per(self):
        if self.discount_method != 'per':
            return

        values = self.get_maximum_per_amount()
        if self.discount_method == 'per' and (
                self.discount_per > 100 or self.discount_per < 0) and \
                values.get('check_group', False):
            raise Warning(_("Percentage should be between 0% to 100%"))
        if self.discount_per > values.get('max_percentage', False) and \
                values.get('check_group', False):
            raise Warning(_("You are not allowed to apply Discount Percentage"
                            " (%s) more than configured Discount Percentage "
                            "(%s) in configuration setting!") % (
                formatLang(self.env,  self.discount_per, digits=2),
                formatLang(self.env, values['max_percentage'], digits=2)))
        config_data = self.env['res.config.settings'].sudo().get_values()
        if config_data.get('global_discount_apply'):
            if config_data.get('global_discount_percentage') < self.discount_per:
                raise Warning(_("You are not allowed to apply Discount "
                                "Percentage (%s) more than configured "
                                "Discount Percentage (%s) in configuration "
                                "setting!") % (
                    formatLang(self.env, self.discount_per, digits=2),
                    formatLang(self.env, config_data.get('global_discount_percentage'),
                               digits=2)))

    @api.onchange('discount_amount')
    def onchange_discount_amount(self):
        if self.discount_method != 'fixed':
            return

        values = self.get_maximum_per_amount()
        if self.discount < 0 < self.gross_amount:
            raise Warning(_("Discount should be less than Gross Amount"))
        if self.discount > 0 > self.gross_amount:
            raise Warning(_("Discount should be less than Gross Amount"))
        discount = self.discount or self.discount_amount
        if (0 < self.gross_amount < discount) or (0 > self.gross_amount > discount):
            raise Warning(_("Discount (%s) should be less than "
                            "Gross Amount (%s).") % (
                formatLang(self.env, discount, digits=2),
                formatLang(self.env, self.gross_amount, digits=2)))
        if self.gross_amount > 0 and self.discount > values.get('max_amount', False) and values.get('check_group', False):
            raise Warning(_("You're not allowed to apply Discount Amount "
                            "(%s) more than configured amount (%s) in "
                            "configuration setting!") % (
                formatLang(self.env, self.discount_amount, digits=2),
                formatLang(self.env, values['max_amount'], digits=2)))
        config_data = self.env['res.config.settings'].sudo().get_values()
        if config_data.get('global_discount_apply'):
            fix_amount = config_data.get('global_discount_fix_amount')
            if self.gross_amount > 0 and fix_amount < self.discount_amount:
                raise Warning(_("You're not allowed to apply Discount "
                                "Amount (%s) more than configured amount "
                                "(%s) in configuration setting!") % (
                    formatLang(self.env, self.discount_amount, digits=2),
                    formatLang(self.env, config_data.get('global_discount_fix_amount'),
                               digits=2)))

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'discount_method': self.discount_method,
            'discount_amount': self.discount_amount,
            'discount_per': self.discount_per,
            'discount': self.discount,
            })
        return invoice_vals
