import logging
from flectra import models, fields, api, _
import flectra.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_type = fields.Selection(
        selection=[
            ('fixed', 'Fixed'),
            ('percent', 'Percent')
        ],
        string="Discount Type",
        default="percent",
    )

    discount_value = fields.Float(
        string='Discount',
        tracking=True,
    )

    discount_value_percent = fields.Float(
        string='Discount (%)',
        digits='Discount',
        compute='_amount_all',
        compute_sudo=True,
    )

    amount_gross = fields.Monetary(
        string='Gross Amount',
        store=True,
        readonly=True,
        compute='_amount_all',
    )

    amount_discountable = fields.Monetary(
        string='Base Discount Amount',
        store=True,
        readonly=True,
        compute='_amount_all',
    )

    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_amount_all',
                                      digits=dp.get_precision('Account'), track_visibility='always')

    document_discount = fields.Monetary(
        string='Document Discount',
        store=True,
        readonly=True,
        compute='_amount_all',
    )

    document_discount_tax_amount = fields.Monetary(
        string='Document Discount Tax',
        store=True,
        readonly=True,
        compute='_amount_all',
    )

    @api.onchange('discount_type', 'discount_value', 'order_line')
    def on_change_discount(self):
        for order in self:
            if order.discount_type == 'percent':
                for line in order.order_line:
                    line.discount = order.discount_value
            else:
                total = 0.0
                for line in order.order_line:
                    total += round((line.product_uom_qty * line.price_unit))
                if order.discount_value != 0:
                    discount = (order.discount_value / total) * 100
                else:
                    discount = order.discount_value
                for line in order.order_line:
                    line.discount = discount

    @api.depends('order_line.price_total', 'order_line.discount')
    def _amount_all(self):
        for order in self:
            amount_untaxed = 0.0
            amount_tax = 0.0
            document_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                document_discount += (line.product_uom_qty * line.price_unit * line.discount) / 100
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'document_discount': document_discount,
                'amount_discount': document_discount,
                'amount_total': amount_untaxed + amount_tax,
            })

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()

        # To apply fixed discount only on first real invoice (no downpayment)
        # we need to check if any real order position was already invoiced
        # real_invoice_exists = len(self.order_line.filtered(lambda f: not f.is_downpayment).invoice_lines.move_id)

        # On fixed document discount we apply the discount only on first invoice
        # On percent document discount the discount is applied on all invoices
        invoice_vals['discount_type'] = self.discount_type
        invoice_vals['discount_value'] = self.discount_value
        return invoice_vals
