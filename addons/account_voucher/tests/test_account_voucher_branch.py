# -*- coding: utf-8 -*-

from datetime import date
from flectra.tests import common
from flectra.api import Environment



class TestAccountVoucherBranch(common.TransactionCase):

    def setUp(self):
        super(TestAccountVoucherBranch, self).setUp()
        self.account_user = self.env.ref('account.group_account_manager')
        self.model_account = self.env['account.account']
        self.main_company = self.env.ref('base.main_company')
        self.model_journal = self.env['account.journal']
        self.partner = self.env.ref('base.res_partner_1')
        self.model_voucher = self.env['account.voucher']
        self.apple_product = self.env.ref('product.product_product_7')
        self.model_voucher_line = self.env['account.voucher.line']
        self.branch_1 = self.env.ref('base_branch_company.data_branch_1')
        self.model_users = self.env['res.users']
        self.branch_2 = self.env.ref('base_branch_company.data_branch_2')
        self.income_type = self.env['account.account.type'].search([('name', '=', 'Income')])
        # account_obj = self.env.ref['account.account']
        self.account_receivable = self.model_account.create(
            {'code': 'X1012', 'name': 'Account Receivable - Test',
             'user_type_id': self.env.ref('account.data_account_type_receivable').id,
             'reconcile': True})
        self.account_1 = self.account_create('acc_code_1', self.income_type.id, self.main_company.id)
        self.account_2 = self.account_create('acc_code_2', self.income_type.id, self.main_company.id)
        self.journal_1 = self.journal_create('journal_code_1', self.account_1, self.main_company.id)
        self.journal_2 = self.journal_create('journal_code_2', self.account_2, self.main_company.id)
        self.branch_user_1 = self.user_create(
            'branch_user_1', self.branch_1, self.main_company,
            [self.branch_1, self.branch_2], [self.account_user])
        self.branch_user_2 = self.user_create('branch_user_2', self.branch_2, self.main_company, [self.branch_2],
                                             [self.account_user])

        self.account_voucher_1 = self.receipt_create(self.journal_1, self.branch_1)
        self.account_voucher_2 = self.receipt_create(self.journal_2, self.branch_2)

    def account_create(self, code, type, company_id):
        data = {'code': code,
                'name': 'Test Sales Account ' + code,
                'company_id': company_id,
                'user_type_id': type,
            }
        account_obj = self.model_account.create(data)
        return account_obj.id

    def journal_create(self, code, account_id, company_id):
        data ={
            'code': code,
            'name': 'Test Sales Account ' + code,
            'type': 'sale',
            'default_debit_account_id': account_id,
            'default_credit_account_id': account_id,
            'company_id': company_id
            }
        journal_obj = self.model_journal.create(data)
        return journal_obj.id

    def user_create(self, user_name, branch_id, company_id, branch_ids, groups_ids ):
        group_ids = [group.id for group in groups_ids]
        data = {
                'login': user_name,
                'name': 'Test User ' + user_name,
                'email': 'demo@yourcompany.com',
                'branch_id':branch_id.id,
                'password': 'test@123',
                'company_id': company_id.id,
                'groups_id': [(6, 0, group_ids)],
                'company_ids': [(4, company_id.id)],
                'branch_ids': [(4, branch.id) for branch in branch_ids],
            }
        user_obj = self.model_users.with_context({'no_reset_password': True}).create(data)
        return user_obj.id

    def receipt_create(self, journal_id, branch_id):
        vals = {
            'name': 'Test Voucher',
            'partner_id': self.partner.id,
            'journal_id': journal_id,
            'voucher_type': 'sale',
            'account_id': self.account_receivable.id,
            'branch_id': branch_id.id,
            'company_id': self.main_company.id,
            'date': date.today(),
        }
        voucher_obj = self.model_voucher.create(vals)
        line_vals = {
            'name': self.apple_product.name,
            'product_id': self.apple_product.id,
            'price_unit': 500,
            'quantity': 10,
            'account_id': self.account_receivable.id,
            'voucher_id': voucher_obj.id,
        }
        self.model_voucher_line.create(line_vals)
        return voucher_obj

