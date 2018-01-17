# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, models, _
from flectra.exceptions import UserError


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields):
        if self._context.get('rma') and self._context.get('active_model') ==\
                'rma.request':
            res = {}
            if len(self.env.context.get('active_ids', list())) > 1:
                raise UserError(_(
                    "You may only replace single picking at a time!"))
            move_dest_exists = False
            product_return_moves = []
            rma_id = self.env['rma.request'].browse(
                self.env.context.get('active_id'))
            picking = rma_id.picking_id
            if picking:
                res.update({'picking_id': picking.id})
                if picking.state != 'done':
                    raise UserError(_("You may only return Done pickings"))

                for move_line in picking.move_lines:
                    qty = move_line.product_qty or 0.00
                    if move_line.move_line_ids:
                        product_ids = [line.product_id for line in
                                       move_line.move_line_ids]
                        vals = {}
                        for rma_line in rma_id.rma_line:
                            vals.update({
                                rma_line.product_id.id: rma_line.qty_replaced,
                            })
                        for prod_id in product_ids:
                            if vals.get(prod_id.id):
                                qty = vals.get(prod_id.id)
                    if move_line.scrapped:
                        continue
                    if move_line.move_dest_ids:
                        move_dest_exists = True
                    quantity = qty - sum(
                        move_line.move_dest_ids.filtered(
                            lambda m: m.state in [
                                'partially_available', 'assigned', 'done']
                        ).mapped('move_line_ids').mapped('product_qty'))
                    product = [line.product_id for line in rma_id.rma_line]
                    for pid in product:
                        if move_line.product_id.id == pid.id:
                            product_return_moves.append(
                                (0, 0,
                                 {
                                     'product_id': move_line.product_id.id,
                                     'quantity': quantity,
                                     'move_id': move_line.id
                                 }))

                if not product_return_moves:
                    raise UserError(_(
                        "No products to replace (only lines in Done state and"
                        "not fully replaced yet can be replaced)!"))
                if 'product_return_moves' in fields:
                    res.update({'product_return_moves': product_return_moves})
                if 'move_dest_exists' in fields:
                    res.update({'move_dest_exists': move_dest_exists})
                if 'parent_location_id' in fields and picking.\
                        location_id.usage == 'internal':
                    res.update(
                        {
                            'parent_location_id':
                                picking.picking_type_id.warehouse_id and
                                picking.picking_type_id.warehouse_id.
                                view_location_id.id or picking.
                                location_id.location_id.id
                        })
                if 'original_location_id' in fields:
                    res.update(
                        {'original_location_id': picking.location_id.id})
                if 'location_id' in fields:
                    location_id = picking.location_id.id
                    if picking.picking_type_id.return_picking_type_id.\
                            default_location_dest_id.return_location:
                        location_id = picking.picking_type_id.\
                            return_picking_type_id.default_location_dest_id.id
                    res['location_id'] = location_id
            return res
        return super(ReturnPicking, self).default_get(fields)

    def create_returns(self):
        if self._context.get('rma') and self._context.get('active_model') == \
                'rma.request':
            rma_id = self.env['rma.request'].browse(
                self.env.context.get('active_id'))
            rma_id.state = 'replacement_created'
        return super(ReturnPicking, self).create_returns()
