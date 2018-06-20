# Part of Flectra. See LICENSE file for full copyright and licensing
# details.

from flectra import api, models, fields
from flectra.exceptions import UserError
from flectra.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    _rec_name = 'product_id'

    blanket_so_line = fields.Boolean(string="Blanket Order", copy=False)
    remaining_to_so_transfer = fields.Float(string="Remaining to Transfer",
                                            copy=False)

    @api.multi
    def _action_launch_procurement_rule(self):
        """
        Launch procurement group run method with required/custom fields
        genrated by a
        sale order line. procurement group will launch '_run_move',
        '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        errors = []
        context = dict(self._context)
        for line in self:
            if line.state != 'sale' or not line.product_id.type in (
                    'consu', 'product') or line.blanket_so_line and \
                    not context.get('blanket'):
                continue
            qty = 0.0
            for move in line.move_ids.filtered(lambda r: r.state != 'cancel'):
                qty += move.product_uom._compute_quantity(move.product_uom_qty,
                                                          line.product_uom,
                                                          rounding_method='HALF-UP')
            if float_compare(qty, line.product_uom_qty,
                             precision_digits=precision) >= 0:
                continue

            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name,
                    'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the
                # order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update(
                        {'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update(
                        {'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)

            if line.blanket_so_line and context.get('blanket'):
                product_qty = context.get('transfer_qty')
            else:
                product_qty = line.product_uom_qty - qty

            procurement_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if procurement_uom.id != quant_uom.id and get_param(
                    'stock.propagate_uom') != '1':
                product_qty = line.product_uom._compute_quantity(product_qty,
                                                                 quant_uom,
                                                                 rounding_method='HALF-UP')
                procurement_uom = quant_uom

            try:
                self.env['procurement.group'].run(line.product_id, product_qty,
                                                  procurement_uom,
                                                  line.order_id.partner_shipping_id.property_stock_customer,
                                                  line.name,
                                                  line.order_id.name, values)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

    @api.multi
    def create(self, vals):
        if vals.get('product_uom_qty') and vals.get('blanket_so_line'):
            vals.update(
                {'remaining_to_so_transfer': vals.get('product_uom_qty')})
        res = super(SaleOrderLine, self).create(vals)
        return res

    @api.multi
    def write(self, values):
        result = super(SaleOrderLine, self).write(values)
        for line in self:
            if 'product_uom_qty' and 'blanket_so_line' in values:
                line.remaining_to_so_transfer = line.product_uom_qty
        return result
