# -*- coding: utf-8 -*-
from flectra.addons.account.tests import test_account_branch
import time


class TestPaymentsBranch(test_account_branch.TestAccountBranch):

    def test_payment_branch(self):
        self.invoice_id = self.model_account_invoice.sudo(self.user_id.id).create(
            self.invoice_values(self.branch_2.id))
        self.invoice_id.sudo(self.user_id.id).action_invoice_open()

        context = {'active_ids': [self.invoice_id.id], 'active_model': 'account.invoice'}
        create_payments = self.env['account.register.payments'].sudo(self.user_id.id).with_context(context).create({
            'payment_method_id': self.env.ref("account.account_payment_method_manual_in").id,
            'journal_id': self.cash_journal.id,
            'payment_date': time.strftime('%Y') + '-12-17',

            })
        create_payments.create_payments()
        payment = self.env['account.payment'].sudo(self.user_2.id).search([('branch_id', '=', self.branch_2.id)])
        self.assertFalse(payment, 'USer 2 should not have access to Payments with Branch %s'
                         % self.branch_2.name)
