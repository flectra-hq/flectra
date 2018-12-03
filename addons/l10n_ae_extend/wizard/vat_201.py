# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models, api, _


class Vat201Report(models.TransientModel):

    _name = "vat.201.report"
    _description = "VAT 201"

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    company_id = fields.Many2one(
        'res.company', string='Company',
        required=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(related='company_id.currency_id')

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        if self.date_from > self.date_to:
            raise ValueError(_("End Date must be greater than "
                               "Start Date!"))

    def print_report(self, data):
        data['form'] = \
            self.read(['date_from', 'date_to', 'company_id', 'currency_id'])[0]
        return self.env.ref('l10n_ae_extend.action_report_vat_201'
                            ).report_action(self, data=data)
