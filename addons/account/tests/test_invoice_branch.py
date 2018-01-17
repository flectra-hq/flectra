# -*- coding: utf-8 -*-
from . import test_account_branch


class TestInvoiceBranch(test_account_branch.TestAccountBranch):

    def test_invoice_create(self):
        self.invoice_id = self.model_account_invoice.sudo(self.user_id.id).create(self.invoice_values(self.branch_2.id))

        invoices = self.model_account_invoice.sudo(self.user_2.id).search([('branch_id', '=', self.branch_2.id)])

        self.assertFalse(invoices, 'USer 2 should not have access to Invoice with Branch %s'
                         % self.branch_2.name)

        self.invoice_id.sudo(self.user_id.id).action_invoice_open()
        all_branch = all(move_line_id.branch_id.id == self.branch_2.id for
                           move_line_id in self.invoice_id.move_id.line_ids)
        self.assertNotEqual(all_branch, False, 'Journal Entries have different Branch.')
