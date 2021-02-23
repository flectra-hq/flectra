import logging
from functools import partial
from flectra import models, fields, api, _
from flectra.tools import float_is_zero, float_round, float_compare
from flectra.tools.misc import formatLang

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
            'discount_type',
            'discount_value',
    )
    def _compute_document_discount(self):
        for move in self:
            document_discount = 0
            discount_used = move.discount_type and not float_is_zero(move.discount_value, precision_digits=move.currency_id.decimal_places)
            if discount_used:
                if move.discount_type == 'fixed':
                    document_discount = move.discount_value * -1
                else:
                    document_discount = (move.amount_gross * (move.discount_value / 100)) * -1

            document_discount = float_round(document_discount, precision_digits=move.currency_id.decimal_places)

            discount_lines = move.line_ids.filtered(lambda f: f.is_document_discount_line)
            if discount_lines:
                document_discount_tax_amount = float_round(
                        sum(line.price_total - line.price_subtotal for line in discount_lines),
                        precision_digits=move.currency_id.decimal_places
                )
            else:
                document_discount_tax_amount = 0
            move.update({
                'document_discount': document_discount,
                'document_discount_tax_amount': document_discount_tax_amount,
                'has_document_discount': discount_used,
                'discount_value_percent': move.discount_value,
            })

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
                amount_gross = sum(move.line_ids.filtered(lambda f: not f.exclude_from_invoice_tab).mapped('price_subtotal'))
                move.update({
                    'amount_gross': amount_gross,
                    'amount_untaxed': move.amount_gross + move.document_discount,
                })
                move._generate_document_discount_move_line()
                move.update({
                    'amount_total': move.amount_untaxed + move.amount_tax,
                })

    def _generate_document_discount_move_line(self):

        aml = self.env['account.move.line'].with_context(check_move_validity=False)

        update_needed = False

        for move in self:

            update_needed = False

            in_draft_mode = move != move._origin
            if float_is_zero(move.document_discount, precision_digits=move.currency_id.decimal_places):
                to_del = move.line_ids.filtered(lambda f: f.is_document_discount_line)
                if in_draft_mode:
                    move.update({'line_ids': [(2, line.id) for line in to_del]})
                    update_needed = True
                continue

            currency = move.currency_id or move.company_id.currency_id
            if move.discount_type == 'fixed':
                account_id = move.company_id.document_discount_fixed_account_id
            else:
                account_id = move.company_id.document_discount_percent_account_id

            create_method = in_draft_mode and aml.new or aml.create
            distributions = move._get_document_tax_distribution()
            for distribution in distributions.values():
                existing_line = move.line_ids.filtered(lambda f: f.is_document_discount_line and f.tax_ids.ids == distribution['tax'].ids)
                balance = currency._convert(
                        move.document_discount * distribution['factor'],
                        move.journal_id.company_id.currency_id,
                        move.journal_id.company_id,
                        move.date or fields.Date.context_today(move),
                )
                price_unit = move.document_discount * distribution['factor']
                amount_currency = price_unit * -1
                if existing_line:
                    line_values = {
                        'amount_currency': amount_currency,
                        'price_unit': price_unit,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                    }
                    if existing_line.credit == line_values['credit'] and existing_line.debit == line_values['debit']:
                        continue

                    update_needed = True
                    if in_draft_mode:
                        existing_line.update(line_values)
                    else:
                        existing_line.write(line_values)
                else:
                    line_values = {
                        'account_id': account_id.id,
                        'amount_currency': amount_currency,
                        'price_unit': price_unit,
                        'currency_id': currency.id,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'name': _('Document Discount'),
                        'move_id': move.id,
                        'partner_id': move.partner_id.id,
                        'company_id': move.company_id.id,
                        'company_currency_id': currency.id,
                        'exclude_from_invoice_tab': True,
                        'is_document_discount_line': True,
                        'tax_ids': distribution['tax'].ids,
                    }
                    create_method(line_values)
                    update_needed = True

        if update_needed:
            self.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)

    def _get_document_tax_distribution(self):
        """
        This function calculates distribution factor for right split
        of negative tax amount of document discount amount.
        @param amount_gross: the base amount (total untaxed amount) used as 100%
        @return: dict with tax.id as key and tax data includin the distribution factor
        """
        self.ensure_one()
        res = {}
        tax_lines = self.line_ids.filtered(lambda f: f.tax_line_id)
        if not tax_lines:
            return res
        total_amount = sum(tax_lines.mapped('tax_base_amount'))
        for line in tax_lines:
            key = line.tax_line_id.id
            res.setdefault(key, {'tax': line.tax_line_id, 'factor': 0.0})
            res[key]['factor'] = line.tax_base_amount / total_amount
        return res

    @api.model_create_multi
    def create(self, vals_list):
        rslt = super(AccountMove, self).create(vals_list)
        rslt._compute_document_discount()
        rslt._compute_amount()
        rslt._generate_document_discount_move_line()
        return rslt


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_document_discount_line = fields.Boolean(help="Technical field used to identify document discount lines.")
