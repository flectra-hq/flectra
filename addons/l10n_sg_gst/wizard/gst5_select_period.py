# Part of Flectra. See LICENSE file for full copyright and licensing
# details.


from flectra import models, fields, api


class WizGst5Report(models.TransientModel):
    _name = 'wiz.gst5.report'
    _description = 'GST5 Report'

    company_id = fields.Many2one('res.company', string='Company',
                                 required=True,
                                 default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)
    answer1_yes = fields.Boolean(string='Yes', default=False)
    answer1_no = fields.Boolean(string='No', default=True)
    answer2_yes = fields.Boolean(string='Yes', default=False)
    answer2_no = fields.Boolean(string='No', default=True)
    answer3_yes = fields.Boolean(string='Yes', default=False)
    answer3_no = fields.Boolean(string='No', default=True)

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        data['taxes'] = self.env.context.get('active_ids', [])
        account_taxes = self.env['account.tax'].browse(data['taxes'])
        data.update({'declaration_of_error': ''})
        datas = {
            'ids': [],
            'model': 'account.tax',
            'form': data
        }
        return self.env.ref('l10n_sg_gst.action_account_gst5_report_id').\
            report_action(account_taxes, data=datas)
