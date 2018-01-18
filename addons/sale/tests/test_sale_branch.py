# -*- coding: utf-8 -*-
from flectra.tests import common


class TestSaleBranch(common.TransactionCase):
    def setUp(self):
        super(TestSaleBranch, self).setUp()

        self.sale_obj = self.env['sale.order']

        self.main_company = self.env.ref('base.main_company')

        self.payment_model_obj = self.env['sale.advance.payment.inv']

        IrModelData = self.env['ir.model.data']
        journal_obj = self.env['account.journal']
        account_obj = self.env['account.account']

        user_type_id = IrModelData.xmlid_to_res_id(
            'account.data_account_type_revenue')
        account_rev_id = account_obj.create(
            {'code': 'X2020', 'name': 'Sales - Test Sales Account',
             'user_type_id': user_type_id, 'reconcile': True})
        user_type_id = IrModelData.xmlid_to_res_id(
            'account.data_account_type_receivable')
        account_recv_id = account_obj.create(
            {'code': 'X1012', 'name': 'Sales - Test Reicv Account',
             'user_type_id': user_type_id, 'reconcile': True})

        self.apple_product = self.env.ref('product.product_product_7')
        self.apple_product.write({'invoice_policy': 'order'})

        # Add account to product
        product_template_id = self.apple_product.product_tmpl_id
        product_template_id.write(
            {'property_account_income_id': account_rev_id})

        self.sale_customer = self.env.ref('base.res_partner_2')
        self.sale_pricelist = self.env.ref('product.list0')

        # Create Sales Journal
        company_id = IrModelData.xmlid_to_res_id('base.main_company') or False
        journal_obj.create(
            {'name': 'Sales Journal - Test', 'code': 'STSJ', 'type': 'sale',
             'company_id': company_id})
        self.sale_customer.write({'property_account_receivable_id': account_recv_id})

        self.sale_user_group = self.env.ref('sales_team.group_sale_manager')
        self.account_user_group = self.env.ref('account.group_account_invoice')
        self.branch_1 = self.env.ref('base_branch_company.data_branch_1')
        self.branch_2 = self.env.ref('base_branch_company.data_branch_2')
        self.branch_3 = self.env.ref('base_branch_company.data_branch_3')



        # self.apple_product = self.env.ref('product.product_product_7')
        # self.apple_product.write({'invoice_policy': 'order'})

        self.user_1 = self.create_sale_user(
            self.main_company, 'user_1', self.branch_1,
            [self.branch_1, self.branch_3],
            [self.sale_user_group, self.account_user_group])
        self.user_2 = self.create_sale_user(
            self.main_company, 'user_2', self.branch_3,
            [self.branch_3], [self.sale_user_group, self.account_user_group])

        self.so_1 = self.create_so(
            self.sale_customer, self.apple_product, self.user_1.id,
            self.branch_1, self.sale_pricelist)
        self.so_2 = self.create_so(
            self.sale_customer, self.apple_product, self.user_2.id,
            self.branch_3, self.sale_pricelist)

    def create_sale_user(self, main_company, user_name,
                         branch_id, branch_ids, groups):
        group_ids = [grp.id for grp in groups]
        data = {
            'company_ids': [(4, main_company.id)],
            'branch_ids': [(4, ou.id) for ou in branch_ids],
            'company_id': main_company.id,
            'groups_id': [(6, 0, group_ids)],
            'default_branch_id': branch_id.id,
            'login': user_name,
            'name': 'Ron Sales User',
            'password': '123',
            'email': 'ron@yourcompany.com',

        }
        user_obj = self.env['res.users'].create(data)
        return user_obj

    def create_so(self, customer_id, product_id,
                  user_id, branch_id, pricelist_id):
        data = {
            'partner_id': customer_id.id,
            'branch_id': branch_id.id,
            'pricelist_id': pricelist_id.id,
            'partner_shipping_id': customer_id.id,
            'partner_invoice_id': customer_id.id,
        }
        sale_id = self.sale_obj.sudo(user_id).create(data)
        self.env['sale.order.line'].sudo(user_id).create({
            'order_id': sale_id.id,
            'product_id': product_id.id,
            'name': 'Order Line'
        })
        return sale_id

    def sale_order_confirm(self, sale_obj):
        context = {
            'open_invoices': True,
            'active_id': sale_obj.id,
            'active_model': 'sale.order',
            'active_ids': sale_obj.ids,

        }
        sale_obj.action_confirm()

        invoice = self.payment_model_obj.create({
            'advance_payment_method': 'all',
        })

        result = invoice.with_context(context).create_invoices()
        invoice = result['res_id']
        return invoice

    def get_sale_order(self, sale_order_id, branch_id):
        sale = self.sale_obj.sudo(self.user_2.id).search(
            [('id', '=', sale_order_id),
             ('branch_id', '=', branch_id)])
        return sale

    def test_user_authentication(self):
        sale = self.get_sale_order(self.so_1.id, self.branch_1.id)
        self.assertEqual(sale.ids, [], 'Test User 2 should not have access to '
                                       'Branch %s' % self.branch_1.name)
        self.sale_order_confirm(self.so_1)
        branch_3_invoice_id = self.sale_order_confirm(self.so_2)
        branch_3 = self.env['account.invoice'].sudo(self.user_2.id).search(
            [('id', '=', branch_3_invoice_id),
             ('branch_id', '=', self.branch_3.id)])
        self.assertNotEqual(branch_3.ids, [],
                            'Invoice should have branch_3 Branch')

    def test_user_authentication_2(self):
        sale = self.get_sale_order(self.so_1.id, self.branch_1.id)
        self.assertEqual(sale.ids, [], 'Test User 2 should '
                                       'not have access to Branch %s'
                         % self.branch_1.name)
        sale = self.get_sale_order(self.so_2.id, self.branch_3.id)
        self.assertEqual(len(sale.ids), 1, 'Test User 1 should'
                                           ' have access to Branch : %s'
                         % self.branch_3.name)
