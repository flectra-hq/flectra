# -*- coding: utf-8 -*-
from flectra.addons.account.tests import test_account_branch
import time


class TestPaymentsBranch(test_account_branch.TestAccountBranch):

    def test_payment_branch(self):
        self.invoice_id = self.model_account_invoice.sudo(self.user_id.id).create(
            self.invoice_values(self.branch_1.id))
        self.invoice_id.sudo(self.user_id.id).action_invoice_open()
        self.journal_model = self.env['account.journal']
        self.account_model = self.env['account.account']
        self.company = self.env.ref('base.main_company')
        user_type = self.env.ref('account.data_account_type_liquidity')
        self.cash1_account_id = self.account_model.create(
            {'name': 'Cash 1 - Test', 'code': 'test_cash_1',
                'user_type_id': user_type.id, 'company_id': self.company.id, })
        self.cash_journal_1 = self.journal_model.create(
            {'name': 'Cash Journal 1 - Test', 'code': 'test_cash_1',
                'type': 'cash', 'company_id': self.company.id,
                'default_debit_account_id': self.cash1_account_id.id,
                'default_credit_account_id': self.cash1_account_id.id,
                'branch_id': self.branch_1.id})
        context = {'active_ids': [self.invoice_id.id], 'active_model': 'account.invoice'}
        create_payments = self.env['account.register.payments'].sudo(self.user_id.id).with_context(context).create({
            'payment_method_id': self.env.ref("account.account_payment_method_manual_in").id,
            'journal_id': self.cash_journal_1.id,
            'payment_date': time.strftime('%Y') + '-12-17',
            })
        create_payments.create_payments()
        payment = self.env['account.payment'].sudo(self.user_2.id).search([('branch_id', '=', self.branch_2.id)])
        self.assertFalse(payment, 'USer 2 should not have access to Payments with Branch %s'
                         % self.branch_2.name)
