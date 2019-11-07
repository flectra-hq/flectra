# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import models, fields, api, _
from flectra.tools.misc import formatLang
from flectra.exceptions import Warning


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.depends('discount_amount', 'discount_per', 'amount_untaxed',
                 'invoice_line_ids')
    def _get_discount(self):
        for record in self:
            total_discount = 0.0
            for invoice_line_id in record.invoice_line_ids:
                total_price = (
                    invoice_line_id.quantity * invoice_line_id.price_unit)
                total_discount += \
                    (total_price * invoice_line_id.discount) / 100
            record.discount = record.currency_id.round(total_discount)

    @api.multi
    @api.depends('invoice_line_ids', 'discount_per', 'discount_amount')
    def _get_total_amount(self):
        for invoice_id in self:
            invoice_id.gross_amount = sum(
                [invoice_id.currency_id.round(line_id.quantity * line_id.price_unit)
                 for line_id in invoice_id.invoice_line_ids])

    discount_method = fields.Selection(
        [('fixed', 'Fixed'), ('per', 'Percentage')], string="Discount Method")
    discount_amount = fields.Float(string="Discount Amount")
    discount_per = fields.Float(string="Discount (%)")
    discount = fields.Monetary(
        string='Discount', readonly=True, compute='_get_discount',
        track_visibility='always')
    gross_amount = fields.Float(string="Gross Amount",
                                compute='_get_total_amount', store=True)

    @api.multi
    def calculate_discount(self):
        for line in self.invoice_line_ids:
            line.write({'discount': 0.0})
        # amount_untaxed = self.amount_untaxed
        gross_amount = self.gross_amount
        if self.discount_method == 'per':
            for line in self.invoice_line_ids:
                line.write({'discount': self.discount_per})
                self._onchange_invoice_line_ids()
        else:
            for line in self.invoice_line_ids:
                discount_value_ratio = \
                    (self.discount_amount * line.price_subtotal) / \
                    gross_amount
                if discount_value_ratio:
                    discount_per_ratio = \
                        (discount_value_ratio * 100) / line.price_subtotal
                    line.write({'discount': discount_per_ratio})
                    self._onchange_invoice_line_ids()
        self._check_constrains()

    @api.multi
    @api.returns('self')
    def refund(self, date_invoice=None,
               date=None, description=None, journal_id=None):
        result = super(AccountInvoice, self).refund(
            date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        result.write({
            'discount_method': result.refund_invoice_id.discount_method,
            'discount_amount': result.refund_invoice_id.discount_amount,
            'discount_per': result.refund_invoice_id.discount_per})
        return result

    @api.constrains('discount_per', 'discount_amount', 'invoice_line_ids')
    def _check_constrains(self):
        self.onchange_discount_per()
        self.onchange_discount_amount()

    @api.onchange('discount_method')
    def onchange_discount_method(self):
        if not self.refund_invoice_id:
            self.discount_amount = 0.0
            self.discount_per = 0.0
        if self.discount_method and not self.invoice_line_ids:
            raise Warning('No Invoice Line(s) were found!')

    @api.multi
    def get_maximum_per_amount(self):
        account_dis_config_obj = self.env['account.discount.config']
        max_percentage = 0
        max_amount = 0
        check_group = False
        for groups_id in self.env.user.groups_id:
            account_dis_config_id = account_dis_config_obj.search(
                [('group_id', '=', groups_id.id)])
            if account_dis_config_id:
                check_group = True
                if account_dis_config_id.percentage > max_percentage:
                    max_percentage = account_dis_config_id.percentage
                if account_dis_config_id.fix_amount > max_amount:
                    max_amount = account_dis_config_id.fix_amount
        return {'max_percentage': max_percentage,
                'max_amount': max_amount, 'check_group': check_group}

    @api.onchange('discount_per')
    def onchange_discount_per(self):
        values = self.get_maximum_per_amount()
        if self.discount_method == 'per' and (
                self.discount_per > 100 or self.discount_per < 0) \
                and values.get('check_group', False):
            raise Warning(_("Percentage should be between 0% to 100%"))
        if self.discount_per > values.get('max_percentage', False) \
                and values.get('check_group', False):
            raise Warning(_("You are not allowed to apply Discount Percentage "
                            "(%s) more than configured Discount Percentage "
                            "(%s) in configuration setting!") % (
                formatLang(self.env,  self.discount_per, digits=2),
                formatLang(self.env, values['max_percentage'], digits=2)))
        config_data = self.env['res.config.settings'].sudo().get_values()
        if config_data.get('global_discount_invoice_apply'):
            global_percentage = config_data.get('global_discount_percentage_invoice')
            if global_percentage < self.discount_per:
                raise Warning(_("You are not allowed to apply Discount "
                                "Percentage(%s) more than configured Discount"
                                " Percentage (%s) in configuration setting!"
                                ) % (
                    formatLang(self.env, self.discount_per, digits=2),
                    formatLang(self.env,
                               config_data.get('global_discount_percentage_invoice'),
                               digits=2)))

    @api.onchange('discount_amount')
    def onchange_discount_amount(self):
        values = self.get_maximum_per_amount()
        if self.discount < 0 < self.gross_amount:
            raise Warning(_("Discount should be less than Gross Amount"))
        if self.discount > 0 > self.gross_amount:
            raise Warning(_("Discount should be less than Gross Amount"))
        discount = self.discount or self.discount_amount
        if discount == 0:
            return
        if (0 < self.gross_amount < discount) or (0 > self.gross_amount > discount):
            raise Warning(_("Discount (%s) should be less than "
                            "Gross Amount (%s).") % (
                formatLang(self.env, discount, digits=2),
                formatLang(self.env, self.gross_amount, digits=2)))
        if self.gross_amount > 0 and self.discount > values.get('max_amount', False) and values.get('check_group', False):
            raise Warning(_("You're not allowed to apply this amount of "
                            "discount as discount Amount (%s) is greater than"
                            " assign Fix Amount (%s).") % (
                formatLang(self.env, self.discount, digits=2),
                formatLang(self.env, values['max_amount'], digits=2)))
        config_data = self.env['res.config.settings'].sudo().get_values()
        if config_data.get('global_discount_invoice_apply'):
            fix_amount = config_data.get('global_discount_fix_invoice_amount')
            if self.gross_amount > 0 and fix_amount < self.discount_amount:
                raise Warning(_("You're not allowed to apply this amount of"
                                " discount as discount Amount (%s) is greater"
                                " than Configuration Amount (%s).") % (
                    formatLang(self.env, self.discount, digits=2),
                    formatLang(self.env,
                               config_data.get('global_discount_fix_invoice_amount'),
                               digits=2)))
