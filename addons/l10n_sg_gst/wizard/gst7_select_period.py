# Part of Flectra. See LICENSE file for full copyright and licensing
# details.


import re

from flectra import models, fields, api, _
from flectra.exceptions import ValidationError


class WizGst7Report(models.TransientModel):
    _name = 'wiz.gst7.report'
    _description = 'GST7 Report'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)
    answer1_yes = fields.Boolean(string='Yes', default=False)
    answer1_no = fields.Boolean(string='No', default=True)
    answer2_yes = fields.Boolean(string='Yes', default=False)
    answer2_no = fields.Boolean(string='No', default=True)
    answer3_yes = fields.Boolean(string='Yes', default=False)
    answer3_no = fields.Boolean(string='No', default=True)
    declaration_of_error = fields.Text(string="Declaration of Errors",
                                       size=200)

    @api.constrains('declaration_of_error')
    def check_declaration_of_error(self):
        if len(self.declaration_of_error) > 200:
            raise ValidationError(
                'Number of characters must on exceed 200')

    def _check_value(self):
        pattern = "^[a-z  A-Z]*$"
        for data in self:
            if re.match(pattern, data.declaration_of_error):
                return True
            else:
                return False
        if len(self.declaration_of_error) > 200:
            raise ValidationError(_(
                'Number of characters must on exceed 200'))
        return {}

    _constraints = [
        (_check_value, 'Please do not enter any symbol in this field".',
         ['declaration_of_error']),
    ]

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        data['taxes'] = self.env.context.get('active_ids', [])
        account_taxes = self.env['account.tax'].browse(data['taxes'])
        datas = {
            'ids': [],
            'model': 'account.tax',
            'form': data
        }
        return self.env.ref(
            'l10n_sg_gst.action_account_gst7_report_id').report_action(
            account_taxes, data=datas)
