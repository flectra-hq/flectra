# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, readonly=True,
                               states={'draft': [('readonly', False)]}, copy=False, tracking=True)
    communication = fields.Char(string='Memo', readonly=True, states={'draft': [('readonly', False)]})
    move_line_ids = fields.One2many('account.move.line', 'payment_id', readonly=True, copy=False)

    def open_payment_matching_screen(self):
        # Open reconciliation view for customers/suppliers
        move_line_id = False
        for move_line in self.move_line_ids:
            if move_line.account_id.reconcile:
                move_line_id = move_line.id
                break
        if not self.partner_id:
            raise UserError(_("Payments without a customer can't be matched"))
        action_context = {'company_ids': [self.company_id.id],
                          'partner_ids': [self.partner_id.commercial_partner_id.id]}
        if self.partner_type == 'customer':
            action_context.update({'mode': 'customers'})
        elif self.partner_type == 'supplier':
            action_context.update({'mode': 'suppliers'})
        if move_line_id:
            action_context.update({'move_line_id': move_line_id})
        return {
            'type': 'ir.actions.client',
            'tag': 'manual_reconciliation_view',
            'context': action_context,
        }
