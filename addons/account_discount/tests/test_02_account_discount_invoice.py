# Part of Flectra See LICENSE file for full copyright and licensing details.

from .test_01_account_discount import TestInvoiceDiscount
import logging


class TestDiscountInvoice(TestInvoiceDiscount):
    def setUp(self):
        super(TestDiscountInvoice, self).setUp()

    def test_01_dp_fixed_amount(self):
        invoice = self.discount_01_set_fixamount()
        invoice.action_invoice_open()

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
