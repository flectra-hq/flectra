# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vat_config_type = fields.Many2one(
        'vat.config.type', 'VAT Type',
        readonly=True, states={'draft': [('readonly', False)]})

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'vat_config_type': self.vat_config_type.id,
            'journal_id': self.vat_config_type.journal_id.id,
            'account_id':
                self.vat_config_type.journal_id.default_debit_account_id.id,
            })
        return invoice_vals

    @api.multi
    @api.onchange('partner_shipping_id', 'partner_id')
    def onchange_partner_shipping_id(self):
        res = super(SaleOrder, self).onchange_partner_shipping_id()
        self.vat_config_type = self.fiscal_position_id.sale_vat_config_type.id
        return res
