# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.
import time
from flectra.addons.purchase.tests import test_purchase_order


class TestPurchaseBranchAuthentication(test_purchase_order.TestPurchaseOrder):
    def setUp(self):
        super(TestPurchaseBranchAuthentication, self).setUp()
        self.user_1 = self.create_test_users(self.main_company, 'user_1', self.branch_1, [self.branch_1],
                                               [self.purchase_user_group, self.stock_user_group])
        self.user_2 = self.create_test_users(self.child_company, 'user_2', self.branch_2, [self.branch_2],
                                               [self.purchase_user_group, self.stock_user_group])
        product_list = [(self.product_id_1, 500),
                        (self.product_id_2, 1000),
                        (self.product_id_3, 800)]
        order_lines = []
        for product_id, quantity in product_list:
            line_values = {
                'name': product_id.name,
                'product_id': product_id.id,
                'price_unit': 80,
                'product_qty': quantity,
                'product_uom': product_id.uom_id.id,
                'date_planned': self.current_time,
            }
            order_lines.append((0, 0, line_values))
        self.purchase = self.PurchaseOrder.sudo(self.user_1).create({
            'partner_id': self.partner_id.id,
            'company_id': self.main_company.id,
            'branch_id': self.branch_1.id,
            'order_line': order_lines,

        })

        self.purchase.sudo(self.user_1).button_confirm()
        self.create_purchase_invoice(self.partner_id, self.purchase,  self.account)

    def create_test_users(self, company_id, login, branch_id, branch_ids, group_ids):
        group_ids = [group_id.id for group_id in group_ids]
        user_obj = \
            self.env['res.users'].with_context({'no_reset_password': True}). \
                create({
                'company_id': company_id.id,
                'company_ids': [(4, company_id.id)],
                'default_branch_id': branch_id.id,
                'branch_ids': [(4, branch.id) for branch in branch_ids],
                'name': 'Alex Purchase User',
                'login': login,
                'password': '123',
                'email': 'alex@yourcompany.com',
                'groups_id': [(6, 0, group_ids)]
            })
        return user_obj.id

    def create_purchase_invoice(self, partner_id, purchase, account):
        context = {
            'active_model': 'purchase.order',
            'active_ids': purchase.ids,
            'active_id': purchase.id,

        }
        invoice_vals = {
            'type': 'in_invoice',
            'partner_id': partner_id.id,
            'purchase_id': purchase.id,
             'account_id': self.partner_id.property_account_payable_id.id,
        }
        self.env['account.invoice'].with_context(context).create(invoice_vals)
        return True
