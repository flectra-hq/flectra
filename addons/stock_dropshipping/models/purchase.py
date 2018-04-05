# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, models, fields, _
from flectra.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    sale_line_id = fields.Many2one('sale.order.line')

    @api.multi
    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for re in res:
            re['sale_line_id'] = self.sale_line_id.id
        return res


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, values, po, supplier):
        res = super(ProcurementRule, self)._prepare_purchase_order_line(product_id, product_qty, product_uom, values, po, supplier)
        res['sale_line_id'] = values.get('sale_line_id', False)
        return res

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.constrains('picking_type_id', 'branch_id')
    def _check_branch(self):
        dropshipping = self.env.ref("stock_dropshipping.picking_type_dropship")
        for order in self:
            warehouse_branch_id = order.picking_type_id.warehouse_id.branch_id
            if order.branch_id and warehouse_branch_id != order.branch_id and order.picking_type_id != dropshipping:
                raise ValidationError(_('Configuration Error of Branch:\n'
                                        'The Purchase Order Branch (%s) and '
                                        'the Warehouse Branch (%s) of Deliver To must '
                                        'be the same branch!') % (
                                      order.branch_id.name,
                                      warehouse_branch_id.name))
