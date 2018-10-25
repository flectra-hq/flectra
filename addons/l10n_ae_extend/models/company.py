# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    rc_vat_account_id = fields.Many2one('account.account', 'Reverse Charge')
    customs_duty_account_id = fields.Many2one(
        'account.account', 'Customs Expense')
    vat_expense_account_id = fields.Many2one('account.account', 'Vat Expense')
