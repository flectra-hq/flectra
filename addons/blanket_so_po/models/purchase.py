# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

from flectra import api, fields, models, _
from flectra.exceptions import Warning


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        if self.order_line.filtered(
                lambda l: l.blanket_po_line):
            raise Warning(
                _('Sorry, You can not cancel blanket line based PO.'))
        self.write({'state': 'cancel'})
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        self.ensure_one()
        context = dict(self._context)
        if self.product_id.type not in ['product',
                                        'consu'] or self.blanket_po_line \
                and not context.get('blanket'):
            return []
        qty = 0.0
        for move in self.move_ids.filtered(
                lambda x: x.state != 'cancel' and not
                x.location_dest_id.usage == "supplier"):
            qty += move.product_uom._compute_quantity(
                move.product_uom_qty, self.product_uom,
                rounding_method='HALF-UP')
        for re in res:
            if self.blanket_po_line and context.get('transfer_qty'):
                re['product_uom_qty'] = context.get('transfer_qty')
            else:
                re['product_uom_qty'] = self.product_qty - qty
        return res

    blanket_po_line = fields.Boolean(string="Blanket Order", copy=False)
    remaining_to_po_transfer = fields.Float(string="Remaining to Transfer",
                                            copy=False)

    @api.multi
    def create(self, vals):
        if vals.get('product_qty') and vals.get('blanket_po_line'):
            vals.update(
                {'remaining_to_po_transfer': vals.get('product_qty')})
        res = super(PurchaseOrderLine, self).create(vals)
        return res

    @api.multi
    def write(self, values):
        result = super(PurchaseOrderLine, self).write(values)
        for line in self:
            if 'product_qty' and 'blanket_po_line' in values:
                line.remaining_to_po_transfer = line.product_qty
        return result
