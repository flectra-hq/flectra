# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vat_config_type = fields.Many2one(
        'vat.config.type', 'VAT Type',
        readonly=True, states={'draft': [('readonly', False)]})
    reverse_charge = fields.Boolean(
        'Reverse Charge', readonly=True,
        states={'draft': [('readonly', False)]})

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self).onchange_partner_id()
        self.vat_config_type = \
            self.fiscal_position_id.purchase_vat_config_type.id
        return res
