# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, fields, api
from flectra.osv import expression


class L10nLatamIdentificationType(models.Model):
    _name = 'l10n_latam.identification.type'
    _description = "Identification Types"
    _order = 'sequence'

    sequence = fields.Integer(default=10)
    name = fields.Char(translate=True, required=True,)
    description = fields.Char()
    active = fields.Boolean(default=True)
    is_vat = fields.Boolean()
    country_id = fields.Many2one('res.country')

    def name_get(self):
        multi_localization = len(self.search([]).mapped('country_id')) > 1
        return [(rec.id, '%s%s' % (
            rec.name, multi_localization and rec.country_id and ' (%s)' % rec.country_id.code or '')) for rec in self]
