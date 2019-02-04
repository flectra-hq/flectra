# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rc_vat_account_id = fields.Many2one('account.account', 'Reverse Charge')
    customs_duty_account_id = fields.Many2one(
        'account.account', 'Customs Expense')
    vat_expense_account_id = fields.Many2one('account.account', 'VAT Expense')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            rc_vat_account_id=self.env.ref('l10n_ae_extend.rc_vat_account').id,
            customs_duty_account_id=self.env.ref(
                'l10n_ae.uae_account_3694').id,
            vat_expense_account_id=self.env.ref(
                'l10n_ae_extend.rc_vat_expense_account').id,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('rc_vat_account_id',
                         self.rc_vat_account_id)
        params.set_param('customs_duty_account_id',
                         self.customs_duty_account_id)
        params.set_param('vat_expense_account_id',
                         self.vat_expense_account_id)
