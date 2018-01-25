# Part of Flectra See LICENSE file for full copyright and licensing details.

from .discount_common import TestDiscountCommon
import logging
import time


class TestInvoiceDiscount(TestDiscountCommon):
    def setUp(self):
        super(TestInvoiceDiscount, self).setUp()

    def discount_01_set_fixamount(self):
        invoice_id = self.AccountInvoice.create({
            'name': 'Discount Invoice Test Fixed',
            'partner_id': self.partner_id.id,
            'currency_id': self.env.ref('base.USD').id,
            'account_id': self.account_id.id,
            'type': 'out_invoice',
            'date_invoice': time.strftime('%Y') + '-03-12',
            'journal_id': self.journal_id.id,
        })
        invoice_id.onchange_discount_method()
        self.AccountInvoiceLine.create({
            'product_id': self.env.ref("product.product_product_10").id,
            'quantity': 10,
            'price_unit': 400,
            'invoice_id': invoice_id.id,
            'name': 'Mouse, Optical',
            'account_id': self.account_id.id,
        })
        self.AccountInvoiceLine.create({
            'product_id': self.env.ref("product.product_product_12").id,
            'quantity': 30,
            'price_unit': 250,
            'invoice_id': invoice_id.id,
            'name': 'Mouse, Wireless',
            'account_id': self.account_id.id,
        })
        invoice_id.write({
            'discount_method': 'fixed',
            'discount_amount': 100,
            })
        self.assertTrue(invoice_id, 'Invoice: no invoice created')
        invoice_id._check_constrains()
        invoice_id.onchange_discount_per()
        invoice_id.onchange_discount_amount()
        logging.info('Successful: Invoice Created!')
        invoice_id.calculate_discount()
        return invoice_id

    def discount_02_set_percentages(self):
        invoice_id = self.AccountInvoice.create({
            'name': 'Discount Invoice Test Percentage',
            'partner_id': self.partner_id.id,
            'currency_id': self.env.ref('base.USD').id,
            'account_id': self.account_id.id,
            'type': 'out_invoice',
            'discount_method': 'per',
            'discount_per': 10,
            'date_invoice': time.strftime('%Y') + '-03-12',
            'journal_id': self.journal_id.id,
        })
        self.AccountInvoiceLine.create({
            'product_id': self.env.ref("product.product_product_10").id,
            'quantity': 10,
            'price_unit': 400,
            'discount': 10,
            'invoice_id': invoice_id.id,
            'name': 'Mouse, Optical',
            'account_id': self.account_id.id,
        })
        self.AccountInvoiceLine.create({
            'product_id': self.env.ref("product.product_product_12").id,
            'quantity': 30,
            'price_unit': 250,
            'discount': 10,
            'invoice_id': invoice_id.id,
            'name': 'Mouse, Wireless',
            'account_id': self.account_id.id,
        })
        return invoice_id

    def account_discount_03_check_include_taxes(self):
        tax_id = self.env['account.tax'].create({
            'name': 'Tax 7.7',
            'amount': 7.7,
            'amount_type': 'percent',
            'price_include': True,
            'include_base_amount': True,
        })

        invoice_id = self.AccountInvoice.create({
            'name': 'Discount Invoice Test Tax Included Price',
            'partner_id': self.partner_id.id,
            'currency_id': self.env.ref('base.USD').id,
            'account_id': self.account_id.id,
            'type': 'out_invoice',
            'date_invoice': time.strftime('%Y') + '-03-12',
            'journal_id': self.journal_id.id,
        })
        invoice_id.onchange_discount_method()
        self.AccountInvoiceLine.create({
            'product_id': self.env.ref("product.product_product_10").id,
            'quantity': 10,
            'price_unit': 400,
            'invoice_id': invoice_id.id,
            'name': 'Mouse, Optical',
            'account_id': self.account_id.id,
            'invoice_line_tax_ids': [(6, 0, [tax_id.id])],
        })
        self.AccountInvoiceLine.create({
            'product_id': self.env.ref("product.product_product_12").id,
            'quantity': 30,
            'price_unit': 250,
            'invoice_id': invoice_id.id,
            'name': 'Mouse, Wireless',
            'account_id': self.account_id.id,
            'invoice_line_tax_ids': [(6, 0, [tax_id.id])],
        })
        invoice_id.write({
            'discount_method': 'fixed',
            'discount_amount': 10,
            })
        self.assertTrue(invoice_id, 'Invoice: no invoice created')
        invoice_id._check_constrains()
        invoice_id.onchange_discount_per()
        invoice_id.onchange_discount_amount()
        logging.info('Successful: Invoice Created!')
        return invoice_id
