# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

from flectra import api, fields, models, _
from flectra.exceptions import ValidationError


class PurchaseTransferProducts(models.TransientModel):
    _name = 'purchase.transfer.products'
    _description = 'Transfer products from Purchase Lines'

    transfer_qty = fields.Float("Transfer Qty")
    ref_id = fields.Many2one('purchase.order.line',
                             string="Product Reference",
                             readonly=True)

    @api.model
    def default_get(self, fields):
        context = dict(self._context)
        result = super(PurchaseTransferProducts, self).default_get(
            fields)
        purchase_line = self.env['purchase.order.line'].browse(
            context.get('active_id'))
        result.update({
            'ref_id': purchase_line.id or False,
            'transfer_qty': purchase_line.remaining_to_po_transfer})
        return result

    @api.multi
    def split_qty_wt_newline_po(self):
        self.ensure_one()
        if self.ref_id.remaining_to_po_transfer < self.transfer_qty:
            raise ValidationError(_(
                'Sorry, You can not transfer more than requested or '
                'remains!'))
        elif self.transfer_qty <= 0:
            raise ValidationError(_(
                'Sorry, You can not transfer zero or negative '
                'quantity!'))
        self.ref_id._create_or_update_picking()
        pickings = self.ref_id.order_id.picking_ids.filtered(
            lambda p: p.state not in ('done', 'cancel'))
        self.ref_id.remaining_to_po_transfer -= self.transfer_qty
        for picking in pickings:
            for line in picking.move_lines.filtered(
                    lambda l: l.product_id.id == self.ref_id.product_id.id and
                    l.purchase_line_id.id == self.ref_id.id):
                total_product_qty = \
                    self.ref_id.remaining_to_po_transfer + \
                    self.ref_id.qty_received
                line.product_uom_qty = \
                    self.ref_id.product_qty - total_product_qty
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
