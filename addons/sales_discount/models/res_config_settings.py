# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    global_discount_per_so_invoice_line = fields.Boolean(
        "Global Discounts",
        implied_group='sales_discount.global_discount_per_so_invoice_line')
    global_discount_apply = fields.Boolean(
        "Do you want to set global discount limit?",
        implied_group='sales_discount.global_discount_apply')
    global_discount_fix_amount = fields.Integer(
        'Fix Amount',
        implied_group='sales_discount.global_discount_apply')
    global_discount_percentage = fields.Integer(
        'Percentage (%)',
        implied_group='sales_discount.global_discount_percentage')

    @api.onchange('global_discount_per_so_invoice_line')
    def onchange_global_discount_per_so_invoice_line(self):
        if not self.global_discount_per_so_invoice_line:
            self.global_discount_apply = False

    @api.onchange('global_discount_apply')
    def onchange_global_discount_apply(self):
        if not self.global_discount_apply:
            self.global_discount_fix_amount = False

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            global_discount_per_so_invoice_line=self.env[
                'ir.config_parameter'].sudo().get_param(
                'global_discount_per_so_invoice_line'),
            global_discount_apply=self.env[
                'ir.config_parameter'].sudo().get_param(
                'global_discount_apply'),
            global_discount_fix_amount=int(self.env[
                'ir.config_parameter'].sudo().get_param(
                'global_discount_fix_amount')),
            global_discount_percentage=int(self.env[
                'ir.config_parameter'].sudo().get_param(
                'global_discount_percentage')),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('global_discount_per_so_invoice_line',
                         self.global_discount_per_so_invoice_line)
        params.set_param('global_discount_apply',
                         self.global_discount_apply)
        params.set_param('global_discount_fix_amount',
                         self.global_discount_fix_amount)
        params.set_param('global_discount_percentage',
                         self.global_discount_percentage)
