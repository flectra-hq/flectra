# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class Account(models.Model):
    _inherit = 'account.account.type'

    activity_type = fields.Selection(
        [('operation_income', 'Operation-Income'),
         ('operation_expense', 'Operation-Expense'),
         ('operation_current_asset', 'Operation-Current Asset'),
         ('operation_current_liability', 'Operation-Cuurent Liability'),
         ('investing', 'Investing'),
         ('financing', 'Financing')], string='Activity Type')
