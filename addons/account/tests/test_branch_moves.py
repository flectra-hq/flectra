# -*- coding: utf-8 -*-
from . import test_account_branch


class TestBranchJournalEntries(test_account_branch.TestAccountBranch):

    def test_branch_security_move_line(self):
        move_ids = self.env['account.move.line'].sudo(self.user_2.id).\
            search([('branch_id', '=', self.branch_2.id)])
        self.assertFalse(move_ids, 'USer 2 should not have access to move lines with Branch %s'
                         % self.branch_2.name)
