# -*- coding: utf-8 -*-
from . import test_account_branch


class TestJournalEntryBranch(test_account_branch.TestAccountBranch):

    def test_journal_entries_branch(self):
        self.sale_journal_id = \
        self.env['account.journal'].search([('type', '=', 'sale')])[0]
        self.account_id = self.env['account.account'].search(
            [('internal_type', '=', 'receivable')])[0]
        move_vals = self.env['account.move'].default_get([])
        lines = [
            (0, 0, {
                'name': 'Test',
                'account_id': self.account_id.id,
                'debit': 0,
                'credit': 100,
                'branch_id': self.branch_1.id,
                }),
            (0, 0, {
                'name': 'Test',
                'account_id': self.account_id.id,
                'debit': 100,
                'credit': 0,
                'branch_id': self.branch_1.id,
            })
        ]
        move_vals.update({
            'journal_id': self.sale_journal_id.id,
            'line_ids': lines,
        })
        move = self.env['account.move'].sudo(self.user_id.id).create(move_vals)
        move.post()

    def _check_balance(self, account_id, acc_type='clearing'):
        domain = [('account_id', '=', account_id)]
        balance = self._get_balance(domain)
        self.assertEqual(balance, 0.0, 'Balance is 0 for all Branch.')
        domain = [('account_id', '=', account_id),
                  ('branch_id', '=', self.branch_2.id)]
        balance = self._get_balance(domain)
        if acc_type == 'other':
            self.assertEqual(balance, -100,
                             'Balance is -100 for Branch.')
        else:
            self.assertEqual(balance, 100,
                             'Balance is 100 for Branch.')
        domain = [('account_id', '=', account_id),
                  ('branch_id', '=', self.branch_3.id)]
        balance = self._get_balance(domain)
        if acc_type == 'other':
            self.assertEqual(balance, 100.0,
                             'Balance is 100 for Branch')
        else:
            self.assertEqual(balance, -100.0,
                             'Balance is -100 for Branch')

    def _get_balance(self, domain):

        aml_rec = self.env['account.move.line'].sudo(self.user_id.id).read_group(domain,['debit', 'credit', 'account_id'], ['account_id'])
        if aml_rec:
            aml_rec = aml_rec[0]
            a = aml_rec.get('debit', 0) - aml_rec.get('credit', 0)
            return a
