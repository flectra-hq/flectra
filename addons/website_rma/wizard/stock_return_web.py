# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _


class StockReturnWeb(models.TransientModel):
    _name = 'stock.return.web'

    order_id = fields.Many2one('sale.order', string='SO Number')
    product_id = fields.Many2one('product.product', string='Product')
    uom_id = fields.Many2one('product.uom', string='UOM')
    qty_return = fields.Float(string='Return Quantity')
    picking_type_id = fields.Many2one('stock.picking.type',
                                      string='Picking Type')
    source_location_id = fields.Many2one('stock.location',
                                         sting='Source Location')
    destination_location_id = fields.Many2one('stock.location',
                                              sting='Destination Location')
    rma_id = fields.Many2one('rma.request', string='Return Request Number')

    @api.model
    def default_get(self, fields):
        res = super(StockReturnWeb, self).default_get(fields)
        return_id = self.env['rma.request'].browse(
            self._context.get('active_id'))
        picking_id = return_id.sale_order_id.picking_ids.filtered(
            lambda pick: pick.state == 'done' and pick.picking_type_id.code ==
            'outgoing').sorted(key=lambda pick_id: pick_id.id)[0]
        res.update({
            'order_id': return_id.sale_order_id and
            return_id.sale_order_id.id or False,
            'rma_id': return_id and return_id.id or False,
            'source_location_id': picking_id.location_dest_id and
            picking_id.location_dest_id.id or False,
            'destination_location_id': picking_id.location_id and
            picking_id.location_id.id or False,
        })

        for line in return_id.rma_line:
            res.update({
                'product_id': line.product_id and line.product_id.id or False,
                'qty_return': line.qty_return or 0.0,
                'uom_id': line.uom_id and line.uom_id.id or False,
            })
        return res

    def return_product(self):
        picking_id = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'partner_id': self.rma_id.partner_id.id,
            'location_id': self.source_location_id.id,
            'location_dest_id': self.destination_location_id.id,
            'rma_id': self.rma_id.id,

        })

        new_move_id = self.env['stock.move'].create({
            'name': _('New Move:') + self.product_id.display_name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.qty_return,
            'product_uom': self.uom_id.id,
            'location_id': self.source_location_id.id,
            'location_dest_id': self.destination_location_id.id,
            'has_tracking': self.product_id.tracking,
            'origin': self.rma_id.name,
            'date': self.rma_id.date,
            'picking_id': picking_id.id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'group_id': self.order_id.procurement_group_id and
            self.order_id.procurement_group_id.id or False
        })
        new_move_id._action_confirm()
        picking_id.action_confirm()

        move_line_id = self.env['stock.move.line'].create({
            'move_id': new_move_id and new_move_id.id or False,
            'product_id': new_move_id.product_id.id,
            'product_uom_id': new_move_id.product_uom.id,
            'date': new_move_id.date,
            'location_id': new_move_id.location_id.id,
            'location_dest_id': new_move_id.location_dest_id.id,
            'product_uom_qty': new_move_id.product_uom_qty or 0.0,
        })

        self.rma_id.state = "rma_created"
