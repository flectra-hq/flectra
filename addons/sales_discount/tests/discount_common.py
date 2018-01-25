# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase


class TestDiscountCommon(TransactionCase):
    def setUp(self):
        super(TestDiscountCommon, self).setUp()
        self.config = self.env['res.config.settings'].create({
            'global_discount_per_so_invoice_line': True,
            'global_discount_apply': True,
            'global_discount_fix_amount': 5000,
            'global_discount_percentage': 50,
        })
        self.config.onchange_global_discount_per_so_invoice_line()
        self.config.onchange_global_discount_apply()
        self.config.set_values()
        self.disc_config_1 = self.env['sale.discount.config'].create({
            'group_id': self.env.ref('sales_team.group_sale_manager').id,
            'fix_amount': 3000.0,
            'percentage': 20.0,
        })
        journal_obj = self.env['account.journal']
        ir_model_data_obj = self.env['ir.model.data']
        self.user_id = self.env.ref('base.user_root')
        self.pricelist_id = self.env.ref('product.list0')
        self.product_1 = \
            self.env.ref('product.product_order_01').product_tmpl_id
        self.product_uom = self.env.ref('product.product_uom_unit')
        self.product_2 = \
            self.env.ref('product.service_order_01').product_tmpl_id
        self.SaleOrderLine = self.env['sale.order.line']
        self.SaleOrder = self.env['sale.order']
        account_acccount_obj = self.env['account.account']
        company_id = \
            ir_model_data_obj.xmlid_to_res_id('base.main_company') or False
        user_type_payable_id = ir_model_data_obj.xmlid_to_res_id(
            'account.data_account_type_payable')
        user_type_receivable_id = ir_model_data_obj.xmlid_to_res_id(
            'account.data_account_type_receivable')
        self.user_type_revenue_id = ir_model_data_obj.xmlid_to_res_id(
            'account.data_account_type_revenue')

        self.account_type_payable_id = account_acccount_obj.create({
            'name': 'Test Payable Account',
            'code': 'TestPA',
            'reconcile': True,
            'user_type_id': user_type_payable_id})

        self.account_type_receivable_id = account_acccount_obj.create({
            'name': 'Test Reiceivable Account',
            'code': 'TestRA',
            'reconcile': True,
            'user_type_id': user_type_receivable_id})

        self.partner_id = self.env['res.partner'].create({
            'name': 'Test Partner',
            'property_account_receivable_id':
                self.account_type_receivable_id.id,
            'email': 'testpartner@test.com',
        })
        self.journal_id = journal_obj.create({
            'name': 'Test Sales Discount Journal ',
            'code': 'JournalSD',
            'type': 'sale',
            'company_id': company_id
        })
        self.product_1.write({
            'property_account_income_id': self.account_type_receivable_id.id})
        self.product_2.write({
            'property_account_income_id': self.account_type_receivable_id.id})
        self.sale_order = self.SaleOrder.create({
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist_id.id,
        })
