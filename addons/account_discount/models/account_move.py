import logging
from functools import partial
from flectra import models, fields, api, _
from flectra.tools import float_is_zero, float_round, float_compare
from flectra.tools.misc import formatLang
from flectra.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

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
        compute='_compute_document_discount',
        compute_sudo=True,
    )

    amount_gross = fields.Monetary(
        string='Gross Amount',
        store=True,
        readonly=True,
        compute='_compute_amount',
    )

    document_discount = fields.Monetary(
        string='Document Discount',
        store=True,
        readonly=True,
        compute='_compute_document_discount',
    )

    document_discount_tax_amount = fields.Monetary(
        string='Document Discount Tax',
        store=True,
        readonly=True,
        compute='_compute_document_discount',
    )

    has_document_discount = fields.Boolean(
        string='Has Document Discount',
        store=True,
        readonly=True,
        compute='_compute_document_discount',
    )

    @api.depends(
        'line_ids.amount_currency',
        'line_ids.price_subtotal',
        'line_ids.price_total',
        'line_ids.product_id',
        'discount_type',
        'discount_value',
    )
    def _compute_document_discount(self):
        for move in self:
            discount_used = move.discount_type and not float_is_zero(move.discount_value,
                                                                     precision_digits=move.currency_id.decimal_places)
            if discount_used:
                amount_gross = 0
                for line in move.invoice_line_ids:
                    amount_gross += line.quantity * line.price_unit

                untaxed_amount = amount_gross
                taxed_amt = 0

                for line in move.line_ids:
                    if line.tax_ids:
                        for tax in line.tax_ids:
                            taxed_amt += line.price_unit * tax.amount / 100
                total_amt = untaxed_amount + taxed_amt

                if move.discount_type == 'fixed':
                    document_discount = move.discount_value
                    if document_discount >= total_amt:
                        raise UserError(_("Discount Cannat be more than or equal to Total Amount"))
                    for line in move.invoice_line_ids:
                        if line.product_id:
                            tax = 0
                            if line.tax_ids:
                                for taxes_line in line.tax_ids:
                                    tax += line.price_unit * taxes_line.amount / 100
                            line_price = line.price_unit + tax
                            discount_value = line_price * document_discount / total_amt
                            discount_ratio = discount_value / line_price * 100
                            if discount_ratio:
                                line.update({
                                    'discount': discount_ratio
                                })
                                move._move_autocomplete_invoice_lines_values()

                else:
                    document_discount = (total_amt * (move.discount_value / 100))

                    if document_discount >= total_amt:
                        raise UserError(_("Discount Cannat be more than or equal to Total Amount"))
                    for line in move.invoice_line_ids:
                        if line.product_id:
                            tax = 0
                            if line.tax_ids:
                                for taxes_line in line.tax_ids:
                                    tax += line.price_unit * taxes_line.amount / 100
                            line_price = line.price_unit + tax
                            discount_value = line_price * document_discount / total_amt
                            discount_ratio = discount_value / line_price * 100
                            if discount_ratio:
                                line.update({
                                    'discount': discount_ratio
                                })
                                move._move_autocomplete_invoice_lines_values()
            else:
                for line in move.invoice_line_ids:
                    line.update({
                        'discount': 0.0
                    })
                    move._move_autocomplete_invoice_lines_values()

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'line_ids.price_total',
        'document_discount',
    )
    def _compute_amount(self):
        super(AccountMove, self)._compute_amount()
        for move in self:
            if move.line_ids:
                amount_gross = sum(
                    move.line_ids.filtered(lambda f: not f.exclude_from_invoice_tab).mapped('price_subtotal'))
                move.update({
                    'amount_gross': amount_gross,
                    'amount_untaxed': amount_gross
                })
                # move._generate_document_discount_move_line()
                move.update({
                    'amount_total': move.amount_untaxed + move.amount_tax,
                })
