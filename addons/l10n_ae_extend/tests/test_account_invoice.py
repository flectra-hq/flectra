# Part of Flectra See LICENSE file for full copyright and licensing details.

from .test_ae_common import TestAECommon
import time
import datetime
from dateutil.relativedelta import relativedelta


class TestAccountInvoice(TestAECommon):
    def setUp(self):
        super(TestAccountInvoice, self).setUp()

    def get_invoice(self, invoice_type, reverse_charge):
        invoice_id = self.AccountInvoice.create({
            'name': 'Test Customer Invoice',
            'partner_id': self.partner_id.id,
            'currency_id': self.env.ref('base.USD').id,
            'account_id': self.account_id.id,
            'type': invoice_type,
            'date_invoice': time.strftime('%Y') + '-03-12',
            'journal_id': self.journal_id.id,
            'vat_config_type': self.config_type_local_sale.id,
            'reverse_charge': reverse_charge,
        })
        self.AccountInvoiceLine.create({
            'product_id': self.product_id.id,
            'quantity': 10,
            'price_unit': 885.00,
            'invoice_id': invoice_id.id,
            'name': 'Graphics Card',
            'account_id': self.account_id.id,
        })
        return invoice_id

    def test_customer_invoice(self):
        invoice_id = self.get_invoice('out_invoice', False)
        line_1 = invoice_id.invoice_line_ids[0]
        line_1.get_invoice_line_account(
            'out_invoice', self.product_id, False, self.main_company)
        self.assertEquals(
            line_1.account_id,
            invoice_id.vat_config_type.journal_id.default_debit_account_id)
        self.assertEquals(
            invoice_id.journal_id, invoice_id.vat_config_type.journal_id)

    def test_vendor_bills(self):
        invoice_id = self.get_invoice('in_invoice', True)
        line_1 = invoice_id.invoice_line_ids[0]
        line_1._onchange_product_id()
        invoice_id._onchange_invoice_line_ids()
        amount_tax = invoice_id.amount_tax
        self.assertEquals(len(invoice_id.tax_line_ids), 1)
        self.assertEquals(len(invoice_id.reverse_tax_line_ids), 0)
        invoice_id.action_invoice_open()
        self.assertEquals(invoice_id.amount_tax, 0)
        self.assertEquals(len(invoice_id.tax_line_ids), 0)
        self.assertEquals(len(invoice_id.reverse_tax_line_ids), 1)
        config_data = self.env['res.config.settings'].sudo().get_values()
        rc_account = config_data.get('rc_vat_account_id') or \
            self.env.ref('l10n_ae_extend.rc_vat_account')
        move_line_id = self.env['account.move.line'].search([
            ('move_id', '=', invoice_id.move_id.id),
            ('account_id', '=', rc_account.id)])
        self.assertEquals(move_line_id.credit, amount_tax)

    def test_report_data(self):
        report_obj = self.env['report.l10n_ae_extend.vat_201']
        date_to = (datetime.date.today() - relativedelta(days=10)
                   ).strftime('%Y-%m-%d')
        date_from = (datetime.date.today() - relativedelta(months=1)
                     ).strftime('%Y-%m-01')
        data = {'form': {
            'date_to': date_to,
            'date_from': date_from,
            'company_id': [self.main_company.id, self.main_company.name],
            'currency_id': [self.main_company.currency_id.id,
                            self.main_company.currency_id.name],
        }}
        dict_data = report_obj.get_report_values(None, data)

        self.assertEquals(
            dict_data['get_local_sale']['amount'], 15930.0)
        self.assertEquals(dict_data['get_local_sale']['tax_amount'], 796.5)
        self.assertEquals(dict_data['get_local_sale']['adjustment'], 4425.00)
        self.assertEquals(
            dict_data['get_local_sale']['return_tax_amount'], 221.25)

        self.assertEquals(dict_data['get_local_purchase']['amount'], 17520)
        self.assertEquals(dict_data['get_local_purchase']['tax_amount'], 876)
        self.assertEquals(dict_data['get_local_purchase']['adjustment'], 8760)
        self.assertEquals(
            dict_data['get_local_purchase']['return_tax_amount'], 438)

        self.assertEquals(
            dict_data['get_reverse_charge_data']['amount'], 17520)
        self.assertEquals(
            dict_data['get_reverse_charge_data']['tax_amount'], 876)
        self.assertEquals(
            dict_data['get_reverse_charge_data']['adjustment'], 4380)
        self.assertEquals(
            dict_data['get_reverse_charge_data']['return_tax_amount'], 219)
        self.assertEquals(round(
            dict_data['get_total_vat_due']['total_tax_amount'], 2), 587.40)
