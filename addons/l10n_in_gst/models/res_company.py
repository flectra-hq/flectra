# Part of Flectra See LICENSE file for full copyright and licensing details.

import time

from flectra import api, fields, models, _
from flectra.exceptions import ValidationError


class Company(models.Model):
    _inherit = 'res.company'

    vat = fields.Char(string='GSTIN', related='partner_id.vat')
    gst_type = fields.Selection([('regular', 'Regular'),
                                 ('unregistered', 'Unregistered'),
                                 ('composite', 'Composite'),
                                 ('volunteer', 'Volunteer')],
                                string='GST Type',
                                related='partner_id.gst_type')
    gst_introduce_date = fields.Date(string='GST Introduce Date',
                                     default=time.strftime('2017-07-01'))
    company_b2c_limit_line = fields.One2many('res.company.b2c.limit',
                                             'company_id', string='B2C Limit')
    rc_gst_account_id = fields.Many2one('account.account', 'Reverse Charge')

    def onchange_state(self, gst_type, vat, state):
        result = {'vat': '', 'country_id': False}
        if gst_type == 'unregistered' and vat:
            result['vat'] = False
        if gst_type != 'unregistered':
            result['vat'] = state.l10n_in_tin
        result['country_id'] = state.country_id and \
            state.country_id.id or False
        return result

    @api.multi
    @api.constrains('vat', 'state_id')
    def _check_gstin_format(self):
        """ Validations for GSTIN number format and length """
        for res in self:
            if res.state_id and res.vat and res.state_id.l10n_in_tin \
                    and res.state_id.l10n_in_tin != res.vat[:2]:
                raise ValidationError(_('Invalid State Code!'))
            if res.vat and len(res.vat) != 15 and res.gst_type != \
                    'unregistered':
                raise ValidationError(_('GSTIN length must be of 15 '
                                        'characters!'))

    @api.onchange('state_id', 'country_id')
    def _onchange_state_id(self):
        """ Set state code as a initial characters of GSTIN """
        result = self.onchange_state(self.gst_type, self.vat, self.state_id)
        self.vat = result['vat']
        self.country_id = result['country_id']

    @api.onchange('gst_type')
    def onchange_gst_type(self):
        """ If gst type is unregistered then GSTIN Number should be blank"""
        if self.gst_type == 'unregistered':
            self.vat = False

    @api.model
    def create(self, vals):
        result = super(Company, self).create(vals)
        result.partner_id.gst_company_partner = True
        if vals.get('state_id', False):
            result.partner_id.state_id = vals['state_id']
        if vals.get('country_id', False):
            result.partner_id.country_id = vals['country_id']
        return result


class CompanyB2CLimit(models.Model):
    _name = 'res.company.b2c.limit'

    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    b2cl_limit = fields.Float(string='B2CL Limit', default=250000.0,
                              help='Inter state minimum limit for B2CL type '
                                   'transactions.')
    b2cs_limit = fields.Float(string='B2CS Limit', default=250000.0,
                              help='Inter state maximum limit for B2CS type '
                                   'transactions.')
    company_id = fields.Many2one('res.company', string='Company')

    @api.constrains('date_to', 'date_from', 'company_id')
    def _check_sheet_date(self):
        for line in self:
            self.env.cr.execute('''
                    SELECT id
                    FROM res_company_b2c_limit
                    WHERE (date_from <= %s and %s <= date_to)
                        AND company_id=%s
                        AND id <> %s''',
                                (line.date_to, line.date_from,
                                 line.company_id.id, line.id))
            if any(self.env.cr.fetchall()):
                raise ValidationError(_(
                    'You cannot have 2 limit lines of same period that '
                    'overlap for %s!') % (line.company_id and
                                          line.company_id.name))

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        if any(self.filtered(lambda line: line.date_from and line.
                             date_to and line.date_from > line.date_to)):
            raise ValidationError(_(
                'From date must be lower than to date.'))
