# -*- coding: utf-8 -*-
from flectra.addons.account.tests.account_test_classes import AccountingTestCase


class TestAccountBranch(AccountingTestCase):
    def setUp(self):
        super(TestAccountBranch, self).setUp()
        self.apple_product = self.env.ref('product.product_product_7')
        self.keyboard_product = self.env.ref('product.product_product_9')
        self.ipod_product = self.env.ref('product.product_product_11')
        self.asset_account = self.env.ref('l10n_generic_coa.conf_stk')
        self.model_account_journal = self.env['account.journal']
        self.model_account = self.env['account.account']
        self.main_company = self.env.ref('base.main_company')
        self.manager_group = self.env.ref('account.group_account_manager')
        self.model_user = self.env['res.users']
        self.model_account_invoice = self.env['account.invoice']
        self.account_partner = self.env.ref('base.res_partner_1')
        self.branch_1 = self.env.ref('base_branch_company.data_branch_1')
        self.branch_2 = self.env.ref('base_branch_company.data_branch_2')
        self.branch_3 = self.env.ref('base_branch_company.data_branch_3')
        user_type = self.env.ref('account.data_account_type_liquidity')
        self.account_type = self.env.ref('account.data_account_type_expenses')

        self.user_id = self.model_user.with_context(
            {'no_reset_password': True}).create({
            'company_id': self.main_company.id,
            'branch_ids': [(4, self.branch_2.id), (4, self.branch_3.id)],
            'company_ids': [(4, self.main_company.id)],
            'groups_id': [(6, 0, [self.manager_group.id])],
            'name': 'Test User 1',
            'email': 'demo@yourcompany.com',
            'password': '123',
            'login': 'tes_user_1',
        })

        self.user_2 = self.model_user.with_context({
            'no_reset_password': True}).create({
            'company_id': self.main_company.id,
            'branch_ids': [(4, self.branch_3.id)],
            'company_ids': [(4, self.main_company.id)],
            'groups_id': [(6, 0, [self.manager_group.id])],
            'name': 'Test  User',
            'email': 'demo@yourcompany.com',
            'password': '123',
            'login': 'test_user_2',
        })

        self.cash_account = self.model_account.create({
            'company_id': self.main_company.id,
            'user_type_id': user_type.id,
            'code': 'cash_test',
            'name': 'Test Cash Account',
        })

        self.cash_journal = self.model_account_journal.create({
            'company_id': self.main_company.id,
            'branch_id': self.branch_1.id,
            'name': 'Cash Journal - Branch 1',
            'default_credit_account_id': self.cash_account.id,
            'default_debit_account_id': self.cash_account.id,
            'type': 'cash',
            'code': 'cash_branch_1',
        })

    def invoice_values(self, branch_id):
        products = [(self.apple_product, 1000),
                    (self.keyboard_product, 500),
                    (self.ipod_product, 800)]
        lines_data = []
        account_id = self.model_account.search([
            ('user_type_id', '=', self.account_type.id)], limit=1).id
        for product_id, quantity in products:
            values = {
                'product_id': product_id.id,
                'name': product_id.name,
                'price_unit': 120,
                'quantity': quantity,
                'account_id': account_id
            }
            lines_data.append((0, 0, values))
        vals = {
            'partner_id': self.account_partner.id,
            'type': 'in_invoice',
            'name': "Supplier Invoice",
            # 'reference_type': "none",
            'account_id': self.account_partner.property_account_payable_id.id,
            'invoice_line_ids': lines_data,
            'branch_id': branch_id,
        }
        return vals
