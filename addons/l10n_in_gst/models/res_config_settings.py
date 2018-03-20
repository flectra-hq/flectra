# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    country_id = fields.Many2one('res.country', string='Country',
                                 compute='_get_gst_details',
                                 inverse='_set_gst_details')
    state_id = fields.Many2one('res.country.state', string='State',
                               domain="[('country_id', '=', country_id)]",
                               compute='_get_gst_details',
                               inverse='_set_gst_details')
    gstin_number = fields.Char(string='GSTIN', size=15,
                               compute='_get_gst_details',
                               inverse='_set_gst_details')
    gst_type = fields.Selection([('regular', 'Regular'),
                                 ('unregistered', 'Unregistered'),
                                 ('composite', 'Composite'),
                                 ('volunteer', 'Volunteer')],
                                string='GST Type',
                                compute='_get_gst_details',
                                inverse='_set_gst_details')
    gst_applied = fields.Boolean(string='GST Applied')

    @api.multi
    @api.depends('company_id', 'gst_applied')
    def _get_gst_details(self):
        """ Get GST configuration details from company """
        self.ensure_one()
        self.country_id = self.company_id.country_id.id
        self.state_id = self.company_id.state_id.id
        self.gstin_number = self.company_id.vat
        self.gst_type = self.company_id.gst_type

    @api.multi
    def _set_gst_details(self):
        """ Set GST configuration details in a company """
        self.ensure_one()
        if self.gst_type:
            partner = self.company_id.partner_id
            partner.write({
                'country_id': self.country_id.id,
                'state_id': self.state_id.id,
                'vat': self.gstin_number,
                'gst_company_partner': True,
            })
            self.company_id.gst_type = self.gst_type

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.gst_applied = False
        if self.company_id and self.company_id.gst_type:
            self.gst_applied = True

    @api.onchange('gstin_number', 'country_id')
    def get_state(self):
        """ Get state value automatically from GSTIN and country """
        if self.gstin_number and self.country_id:
            state_code = self.gstin_number[:2]
            state_id = self.env['res.country.state'].search([
                ('l10n_in_tin', '=', state_code),
                ('country_id', '=', self.country_id.id)])
            self.state_id = state_id

    @api.onchange('gst_type')
    def onchange_gst_type(self):
        """ If gst type is unregistered then GSTIN Number should be blank"""
        if self.gst_type == 'unregistered':
            self.gstin_number = False
