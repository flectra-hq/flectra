# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase


class TestGSTCommon(TransactionCase):
    def setUp(self):
        super(TestGSTCommon, self).setUp()

        self.account_invoice_b2b = self.env.ref(
            'l10n_in_gst.demo_invoice_gst9')

        self.account_invoice_b2cs = self.env.ref(
            'l10n_in_gst.demo_invoice_gst10')
        self.b2c_limit_b2cs = self.env['res.company.b2c.limit'].search([
            ('date_from', '<=', self.account_invoice_b2cs.date_invoice),
            ('date_to', '>=', self.account_invoice_b2cs.date_invoice),
            ('company_id', '=', self.account_invoice_b2cs.company_id.id)])

        self.account_invoice_b2cl = self.env.ref(
            'l10n_in_gst.demo_invoice_gst8')
        self.b2c_limit_b2cl = self.env['res.company.b2c.limit'].search([
            ('date_from', '<=', self.account_invoice_b2cl.date_invoice),
            ('date_to', '>=', self.account_invoice_b2cl.date_invoice),
            ('company_id', '=', self.account_invoice_b2cl.company_id.id)])

        self.account_invoice_composite = self.env.ref(
            'l10n_in_gst.demo_invoice_gst11')

        self.res_partner_registered = self.env.ref(
            'l10n_in_gst.res_partner_gst_registered')
        self.res_partner_unregistered = self.env.ref(
            'l10n_in_gst.res_partner_gst_unregistered')

        self.demo_company = self.env.ref('base.main_company')

        self.tax_gst_5 = self.env['account.tax'].create({
            'name': 'Test-GST 5%',
            'type_tax_use': 'sale',
            'amount': 5
        })
        self.tax_gst_18 = self.env['account.tax'].create({
            'name': 'Test-GST 18%',
            'type_tax_use': 'sale',
            'amount': 18
        })
        self.tax_igst_5 = self.env['account.tax'].create({
            'name': 'Test-IGST 5%',
            'type_tax_use': 'sale',
            'amount': 5
        })
        self.tax_igst_28 = self.env['account.tax'].create({
            'name': 'Test-IGST 28%',
            'type_tax_use': 'sale',
            'amount': 28
        })
