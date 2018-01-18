# -*- coding: utf-8 -*-
# Part of Odoo,Flectra. See LICENSE file for full copyright and licensing details.
from flectra.addons.purchase.tests import \
    test_purchase_branch


class TestUserAuthorization(test_purchase_branch.TestPurchaseBranchAuthentication):
    def test_user_authorization(self):

        purchase_ids = self.PurchaseOrder.sudo(self.user_2).search([('branch_id', '=', self.branch_1.id)]).ids
        self.assertEqual(purchase_ids, [], 'User %s wrongly accessed Purchase order %s ' % (self.user_2, str(purchase_ids)))
        picking_ids = self.env['stock.picking'].sudo(self.user_2).search([('id', 'in', self.purchase.picking_ids.ids)]).ids
        self.assertEqual(picking_ids, [], 'User %s wrongly accessed Pickings %s ' % (self.user_2, str(picking_ids)))
        invoice_ids = self.AccountInvoice.sudo(self.user_2).search([('purchase_id', '=', self.purchase.id)]).ids
        self.assertEqual(invoice_ids, [], 'User %s wrongly accessed Invoices %s ' % (self.user_2, str(invoice_ids)))

        purchase_ids = self.PurchaseOrder.sudo(self.user_1).search([('branch_id', '=', self.branch_1.id)]).ids
        self.assertNotEqual(purchase_ids, [], 'User %s Should have accessed to Purchase Orders %s ' % (self.user_1, str(purchase_ids)))
        picking_ids = self.env['stock.picking'].sudo(self.user_1).search([('id', 'in', self.purchase.picking_ids.ids)]).ids
        self.assertNotEqual(picking_ids, [], 'User %s Should have accessed to Pickings %s ' % (self.user_1, str(picking_ids)))
        invoice_ids = self.AccountInvoice.sudo(self.user_1).search([('purchase_id', '=', self.purchase.id)]).ids
        self.assertNotEqual(invoice_ids, [], 'User %s Should have accessed to Invoices %s ' % (self.user_1, str(invoice_ids)))
