# -*- coding: utf-8 -*-

from . import test_account_voucher_branch as test_branch


class TestAccountVoucherReceiptBranch(test_branch.TestAccountVoucherBranch):

    def test_account_receipt_voucher(self):

        self.account_voucher_1.proforma_voucher()
        self.account_voucher_2.proforma_voucher()

        branch_1_ids = all(line_id_1.branch_id.id == self.account_voucher_1.branch_id.id
            for line_id_1 in self.account_voucher_1.move_id.line_ids)
        branch_2_ids = all(line_id_2.branch_id.id == self.account_voucher_2.branch_id.id
            for line_id_2 in self.account_voucher_2.move_id.line_ids)
        self.assertNotEqual(branch_1_ids, False, 'Journal Entries of receipt has different branch id.')
        self.assertNotEqual(branch_2_ids, False, 'Journal Entries of receipt has different branch id.')

        self.account_move = self.env['account.move']
        account_move_id_1 = self.account_voucher_1.move_id
        account_move_id_2 = self.account_voucher_2.move_id
        account_move_ids = self.account_move.sudo(self.branch_user_1).search(
            [('id', 'in', [account_move_id_1.id, account_move_id_2.id])])
        self.assertEqual(len(account_move_ids), 2)

        account_move_ids = self.account_move.sudo(self.branch_user_2).search(
            [('id', 'in', [account_move_id_1.id, account_move_id_2.id]),
             ('branch_id', '=', self.branch_2.id)])
        self.assertEqual(len(account_move_ids), 1)
