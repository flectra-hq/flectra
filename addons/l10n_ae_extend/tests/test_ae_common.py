# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase


class TestAECommon(TransactionCase):
    def setUp(self):
        super(TestAECommon, self).setUp()

        self.AccountInvoice = self.env['account.invoice']
        self.AccountInvoiceLine = self.env['account.invoice.line']
        self.config_type_local_sale = \
            self.env.ref('l10n_ae_extend.config_type_1')
        self.config_type_inside_gcc = \
            self.env.ref('l10n_ae_extend.config_type_2')
        self.main_company = self.env.ref('base.main_company')

        self.partner_id = self.env.ref('base.res_partner_3')
        self.account_id = self.env.ref('l10n_ae_extend.local_sale_uae_account')
        self.journal_id = self.env.ref('l10n_ae_extend.local_sale_journal')
        self.product_id = self.env.ref('product.product_product_24')

        self.customer_tax_id = self.env.ref('l10n_ae.sale_uae_vat_5')
        self.supplier_tax_id = self.env.ref('l10n_ae.purchase_uae_vat_5')
        self.product_id.write({
            'taxes_id': [(6, 0, [self.customer_tax_id.id])],
            'supplier_taxes_id': [(6, 0, [self.supplier_tax_id.id])]})
