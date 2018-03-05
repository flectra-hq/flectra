# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.exceptions import UserError


class RMALine(models.Model):
    _name = "rma.line"
    _description = "RMA Line"

    product_id = fields.Many2one('product.product', string='Product')
    uom_id = fields.Many2one('product.uom', string='UOM')
    qty_delivered = fields.Float(string='Delivered Quantity')
    qty_return = fields.Float(string='Return Quantity')
    rma_id = fields.Many2one('rma.request', string='RMA Request Number')
    move_line_id = fields.Many2one('stock.move', string='Stock Move')
    reason_id = fields.Many2one("return.reason", sting='Reason for RMA')
    remark = fields.Text(sting='Remark')
    team_id = fields.Many2one('crm.team', 'Team', related='rma_id.team_id')

    @api.onchange('qty_return')
    def _onchange_qty_return(self):
        if not self.rma_id.is_website and self.product_id.tracking != 'none':
            can_be_return_qty = sum(line.qty_done for line in
                                    self.move_line_id.move_line_ids if
                                    line.lot_id.warranty_date and
                                    line.lot_id.warranty_date >=
                                    self.rma_id.date)
            if self.qty_return > can_be_return_qty:
                raise UserError(_('You can only return %s quantity for '
                                  'product %s as its warranty has been '
                                  'expired.') % (can_be_return_qty,
                                                 self.product_id.name))
        elif self.qty_return > self.qty_delivered:
            raise UserError(_('Return quantity of %s should not be '
                              'greater than ordered quantity.') %
                            (self.product_id.name))

        if self.qty_return == 0:
            raise UserError(_('Return quantity should not be 0.'))
