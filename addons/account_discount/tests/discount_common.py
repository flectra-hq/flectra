# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase


class TestDiscountCommon(TransactionCase):
    def setUp(self):
        super(TestDiscountCommon, self).setUp()
        self.config = self.env['res.config.settings'].create({
            'global_discount_invoice_line': True,
            'global_discount_invoice_apply': True,
            'global_discount_fix_invoice_amount': 5000,
            'global_discount_percentage_invoice': 50,
        })
        self.config.onchange_global_discount_invoice_line()
        self.config.onchange_global_discount_invoice_apply()
        self.config.set_values()
        self.disc_config_1 = self.env['account.discount.config'].create({
            'group_id': self.env.ref('account.group_account_user').id,
            'fix_amount': 3000.0,
            'percentage': 20.0,
        })
        ir_model_data_obj = self.env['ir.model.data']
        AccountAccount = self.env['account.account']
        AccountJournal = self.env['account.journal']
        self.AccountInvoice = self.env['account.invoice']
        self.AccountInvoiceLine = self.env['account.invoice.line']
        company_id = \
            ir_model_data_obj.xmlid_to_res_id('base.main_company') or False
        user_type_payable_id = ir_model_data_obj.xmlid_to_res_id(
            'account.data_account_type_payable')
        user_type_receivable_id = ir_model_data_obj.xmlid_to_res_id(
            'account.data_account_type_receivable')
        self.user_type_revenue_id = ir_model_data_obj.xmlid_to_res_id(
            'account.data_account_type_revenue')

        self.account_type_payable_id = AccountAccount.create({
            'name': 'Test Payable Account',
            'code': 'TestPA',
            'reconcile': True,
            'user_type_id': user_type_payable_id})

        self.account_type_receivable_id = AccountAccount.create({
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

        self.journal_id = AccountJournal.create({
            'name': 'Test Journal',
            'code': 'Journal001',
            'type': 'sale',
            'company_id': company_id})

        self.account_id = AccountAccount.create({
            'name': 'Test',
            'code': 'DA',
            'user_type_id': self.user_type_revenue_id,
            })
