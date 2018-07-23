# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.exceptions import ValidationError


class Partner(models.Model):
    """ Inherit Partner """
    _inherit = 'res.partner'

    gst_company_partner = fields.Boolean(string='Is company partner?')
    gst_type = fields.Selection([('regular', 'Regular'),
                                 ('unregistered', 'Unregistered'),
                                 ('composite', 'Composite'),
                                 ('volunteer', 'Volunteer')],
                                string='GST Type')
    e_commerce = fields.Boolean(string='E-Commerce')
    partner_location = fields.Selection([('inter_state', 'Inter State'),
                                         ('intra_state', 'intra State'),
                                         ('inter_country', 'Inter Country')
                                         ], "Partner Location")
    property_account_position_id = fields.Many2one(
            'account.fiscal.position',
            company_dependent=True,
            string="Nature of Transaction",
            help="The fiscal position will determine taxes and accounts "
                 "used for the partner.",
            oldname="property_account_position")

    @api.multi
    @api.constrains('vat', 'state_id')
    def _check_gstin_format(self):
        for res in self:
            if res.state_id and res.vat and res.state_id.l10n_in_tin \
                    and res.state_id.l10n_in_tin != res.vat[:2]:
                raise ValidationError(_('Invalid State Code!'))
            if res.vat and len(res.vat) != 15 and res.gst_type != \
                    'unregistered':
                raise ValidationError(_('GSTIN length must be of 15 '
                                        'characters!'))

    def _get_partner_location_details(self, company):
        partner_location = False
        if self.country_id and company.country_id:
            partner_location = 'inter_country'
            if self.country_id.id == company.country_id.id:
                partner_location = 'inter_state'
                if self.state_id and company.state_id and self.state_id.id == \
                        company.state_id.id:
                    partner_location = 'intra_state'
        return partner_location

    @api.onchange('state_id', 'property_account_position_id', 'country_id')
    def _onchange_state_id(self):
        """ Set state code as a initial characters of GSTIN """
        result = self.company_id.onchange_state(self.gst_type, self.vat,
                                                self.state_id)
        self.vat = result['vat']
        self.country_id = result['country_id']
        self.partner_location = self._get_partner_location_details(
            self.company_id)
        if self.state_id == self.env.user.company_id.state_id and \
                self.property_account_position_id:
            self.property_account_position_id = False
            return {
                'warning': {
                    'title': 'Warning',
                    'message': 'Fiscal Position not needed for '
                               'same state Customers!'
                    }
                }

    @api.onchange('gst_type')
    def onchange_gst_type(self):
        """
        If gst type is unregistered then GSTIN Number should be blank
        """
        if self.gst_type == 'unregistered':
            self.vat = False
