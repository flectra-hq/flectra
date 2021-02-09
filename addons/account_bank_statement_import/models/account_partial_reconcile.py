# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from collections import defaultdict
from flectra.tools import float_is_zero


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    currency_id = fields.Many2one('res.currency', string='Currency')
    amount_currency = fields.Monetary(string="Amount in Currency")

    def create_tax_cash_basis_entry(self, percentage_before_rec):
        self.ensure_one()
        move_date = self.debit_move_id.date
        newly_created_move = self.env['account.move']
        cash_basis_amount_dict = defaultdict(float)
        cash_basis_base_amount_dict = defaultdict(float)
        cash_basis_amount_currency_dict = defaultdict(float)
        # We use a set here in case the reconciled lines belong to the same move (it happens with POS)
        for move in {self.debit_move_id.move_id, self.credit_move_id.move_id}:
            # move_date is the max of the 2 reconciled items
            if move_date < move.date:
                move_date = move.date
            percentage_before = percentage_before_rec[move.id]
            percentage_after = move.line_ids[0]._get_matched_percentage()[move.id]
            # update the percentage before as the move can be part of
            # multiple partial reconciliations
            percentage_before_rec[move.id] = percentage_after

            for line in move.line_ids:
                if not line.tax_exigible:
                    # amount is the current cash_basis amount minus the one before the reconciliation
                    amount = line.balance * percentage_after - line.balance * percentage_before
                    rounded_amt = self._get_amount_tax_cash_basis(amount, line)
                    if float_is_zero(rounded_amt, precision_rounding=line.company_id.currency_id.rounding):
                        continue
                    if line.tax_line_id and line.tax_line_id.tax_exigibility == 'on_payment':
                        if not newly_created_move:
                            newly_created_move = self._create_tax_basis_move()
                        # create cash basis entry for the tax line
                        to_clear_aml = self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'name': line.move_id.name,
                            'debit': abs(rounded_amt) if rounded_amt < 0 else 0.0,
                            'credit': rounded_amt if rounded_amt > 0 else 0.0,
                            'account_id': line.account_id.id,
                            'analytic_account_id': line.analytic_account_id.id,
                            'analytic_tag_ids': line.analytic_tag_ids.ids,
                            'tax_exigible': True,
                            'amount_currency': line.amount_currency and line.currency_id.round(
                                -line.amount_currency * amount / line.balance) or 0.0,
                            'currency_id': line.currency_id.id,
                            'move_id': newly_created_move.id,
                            'partner_id': line.partner_id.id,
                            'journal_id': newly_created_move.journal_id.id,
                        })
                        # Group by cash basis account and tax
                        self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'name': line.name,
                            'debit': rounded_amt if rounded_amt > 0 else 0.0,
                            'credit': abs(rounded_amt) if rounded_amt < 0 else 0.0,
                            'account_id': line.tax_repartition_line_id.account_id.id or line.account_id.id,
                            'analytic_account_id': line.analytic_account_id.id,
                            'analytic_tag_ids': line.analytic_tag_ids.ids,
                            'tax_exigible': True,
                            'amount_currency': line.amount_currency and line.currency_id.round(
                                line.amount_currency * amount / line.balance) or 0.0,
                            'currency_id': line.currency_id.id,
                            'move_id': newly_created_move.id,
                            'partner_id': line.partner_id.id,
                            'journal_id': newly_created_move.journal_id.id,
                            'tax_repartition_line_id': line.tax_repartition_line_id.id,
                            'tax_base_amount': line.tax_base_amount,
                            'tag_ids': [(6, 0, line._convert_tags_for_cash_basis(line.tag_ids).ids)],
                        })
                        if line.account_id.reconcile and not line.reconciled:
                            # setting the account to allow reconciliation will help to fix rounding errors
                            to_clear_aml |= line
                            to_clear_aml.reconcile()
                    else:
                        # create cash basis entry for the base
                        for tax in line.tax_ids.flatten_taxes_hierarchy().filtered(
                                lambda tax: tax.tax_exigibility == 'on_payment'):
                            # We want to group base lines as much as
                            # possible to avoid creating too many of them.
                            # This will result in a more readable report
                            # tax and less cumbersome to analyse.
                            key = self._get_tax_cash_basis_base_key(tax, move, line)
                            cash_basis_amount_dict[key] += rounded_amt
                            cash_basis_base_amount_dict[key] += line.tax_base_amount
                            cash_basis_amount_currency_dict[key] += line.currency_id.round(
                                line.amount_currency * amount / line.balance) if line.currency_id and self.amount_currency else 0.0

        if cash_basis_amount_dict:
            if not newly_created_move:
                newly_created_move = self._create_tax_basis_move()
            self._create_tax_cash_basis_base_line(cash_basis_amount_dict, cash_basis_amount_currency_dict,
                                                  cash_basis_base_amount_dict, newly_created_move)
        if newly_created_move:
            self._set_tax_cash_basis_entry_date(move_date, newly_created_move)
            # post move
            newly_created_move.post()
