# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _default_config_type(self):
        return self.vat_config_type.search([
            ('journal_id.type', '=', 'purchase')], limit=1)

    vat_config_type = fields.Many2one(
        'vat.config.type', 'VAT Type', default=_default_config_type,
        readonly=True, states={'draft': [('readonly', False)]})
    reverse_charge = fields.Boolean(
        'Reverse Charge', readonly=True,
        states={'draft': [('readonly', False)]})
