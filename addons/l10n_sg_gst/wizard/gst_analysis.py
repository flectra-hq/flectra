# Part of Flectra. See LICENSE file for full copyright and licensing
# details.


from flectra import models, fields, api


class WizGstAnalysis(models.TransientModel):
    _name = 'wiz.gst.analysis'
    _description = 'GST Analysis'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string="From", required=True)
    date_to = fields.Date(string="To", required=True)

    @api.multi
    def print_report(self):
        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(
            ['company_id', 'date_from', 'date_to'])
        res = res and res[0] or {}
        datas['form'] = res
        return self.env.ref(
            'l10n_sg_gst.action_account_gst_analysis').report_action([],
                                                                    data=datas)
