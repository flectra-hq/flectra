# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, api, _, fields


class account_journal(models.Model):
    _inherit = "account.journal"

    default_debit_account_id = fields.Many2one('account.account', string='Default Debit Account',
                                               domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
                                               help="It acts as a default account for debit amount",
                                               ondelete='restrict')
    default_credit_account_id = fields.Many2one('account.account', string='Default Credit Account',
                                                domain=[('deprecated', '=', False)],
                                                help="It acts as a default account for credit amount",
                                                ondelete='restrict')
    post_at = fields.Selection([('pay_val', 'Payment Validation'), ('bank_rec', 'Bank Reconciliation')],
                               string="Post At", default='pay_val')

    def action_open_reconcile(self):
        if self.type in ['bank', 'cash']:
            # Open reconciliation view for bank statements belonging to this journal
            bank_stmt = self.env['account.bank.statement'].search([('journal_id', 'in', self.ids)]).mapped('line_ids')
            return {
                'type': 'ir.actions.client',
                'tag': 'bank_statement_reconciliation_view',
                'context': {'statement_line_ids': bank_stmt.ids, 'company_ids': self.mapped('company_id').ids},
            }
        else:
            # Open reconciliation view for customers/suppliers
            action_context = {'show_mode_selector': False, 'company_ids': self.mapped('company_id').ids}
            if self.type == 'sale':
                action_context.update({'mode': 'customers'})
            elif self.type == 'purchase':
                action_context.update({'mode': 'suppliers'})
            return {
                'type': 'ir.actions.client',
                'tag': 'manual_reconciliation_view',
                'context': action_context,
            }
