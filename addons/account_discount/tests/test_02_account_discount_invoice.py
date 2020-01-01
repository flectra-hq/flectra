# Part of Flectra See LICENSE file for full copyright and licensing details.

from .test_01_account_discount import TestInvoiceDiscount
import datetime
import logging


class TestDiscountInvoice(TestInvoiceDiscount):
    def setUp(self):
        super(TestDiscountInvoice, self).setUp()

    def test_01_dp_fixed_amount(self):
        invoice = self.discount_01_set_fixamount()
        invoice.action_invoice_open()

    def test_04_dp_refund_fixed_amount(self):
        invoice = self.discount_01_set_fixamount()
        invoice.action_invoice_open()
        context = {"active_model": 'account.invoice', "active_ids": [invoice.id], "active_id": invoice.id}
        account_invoice_refund_2 = self.env['account.invoice.refund'].with_context(context).create(dict(
            description='Refund for Invoice',
            filter_refund='refund'
        ))

        account_invoice_refund_2.with_context(context).invoice_refund()
        invoice.refund_invoice_ids and invoice.refund_invoice_ids[0].action_invoice_open()
        self.assertEqual(invoice.refund_invoice_ids[0].discount_method, invoice.discount_method, "Discount method is fix")
        self.assertEqual(invoice.refund_invoice_ids[0].discount_amount, invoice.discount_amount, "Discount Amount is equal")

    def test_02_percentage_discount(self):
        invoice_id = self.discount_02_set_percentages()
        invoice_id._check_constrains()
        invoice_id.onchange_discount_per()
        invoice_id.onchange_discount_amount()
        self.assertTrue(invoice_id, 'Invoice: no invoice created')
        logging.info('Successful: Invoice Created!')
        invoice_id.write({
            'discount_method': 'per',
            'discount_per': 20.0,
        })
        invoice_id.calculate_discount()
        invoice_id.action_invoice_open()

    def test_03_fixed_discount_include_taxes(self):
        invoice_id = self.account_discount_03_check_include_taxes()
        invoice_id.calculate_discount()
        self.assertEquals(10, round(invoice_id.discount),
                          'Discount Calculation error')
        invoice_id.action_invoice_open()

    def test_05_dp_refund_percentage_discount(self):
        invoice = self.discount_02_set_percentages()
        invoice.action_invoice_open()
        context = {"active_model": 'account.invoice', "active_ids": [invoice.id], "active_id": invoice.id}
        account_invoice_refund_2 = self.env['account.invoice.refund'].with_context(context).create(dict(
            description='Refund for Invoice',
            filter_refund='refund'
        ))
        account_invoice_refund_2.with_context(context).invoice_refund()
        invoice.refund_invoice_ids and invoice.refund_invoice_ids[0].action_invoice_open()
        self.assertEqual(invoice.refund_invoice_ids[0].discount_method, invoice.discount_method, "Discount method is percentage")
        self.assertEqual(invoice.refund_invoice_ids[0].discount_per, invoice.discount_per, "Discount percentage is equal")