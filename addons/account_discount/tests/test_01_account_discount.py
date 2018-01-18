# Part of Flectra See LICENSE file for full copyright and licensing details.

from .discount_common import TestDiscountCommon
import logging
import time


class TestInvoiceDiscount(TestDiscountCommon):
    def setUp(self):
        super(TestInvoiceDiscount, self).setUp()

    def discount_01_set_fixamount(self):

        self.account_id = self.env['account.account'].create({
            'name': 'Test',
            'code': 'DA',
            'user_type_id': self.user_type_revenue_id,
            })

        invoice_id = self.env['account.invoice'].create({
            'name': 'Discount Invoice Test Fixed',
            'partner_id': self.partner_id.id,
            'currency_id': self.env.ref('base.USD').id,
            'account_id': self.account_id.id,
            'type': 'out_invoice',
            'date_invoice': time.strftime('%Y') + '-03-12',
            'journal_id': self.journal_id.id,
        })
        invoice_id.onchange_discount_method()
        invoice_id.write({
            'discount_method': 'fixed',
            'discount_amount': 100,
            })
        self.env['account.invoice.line'].create({
            'product_id': self.env.ref("product.product_product_10").id,
            'quantity': 10,
            'price_unit': 400,
            'invoice_id': invoice_id.id,
            'name': 'Mouse, Optical',
            'account_id': self.account_id.id,
        })
        self.env['account.invoice.line'].create({
            'product_id': self.env.ref("product.product_product_12").id,
            'quantity': 30,
            'price_unit': 250,
            'invoice_id': invoice_id.id,
            'name': 'Mouse, Wireless',
            'account_id': self.account_id.id,
        })
        self.assertTrue(invoice_id, 'Invoice: no invoice created')
        invoice_id._check_constrains()
        invoice_id.onchange_discount_per()
        invoice_id.onchange_discount_amount()
        logging.info('Successful: Invoice Created!')
        invoice_id.calculate_discount()
        return invoice_id

    def discount_02_set_percentages(self):
        self.account_id = self.env['account.account'].create({
            'name': 'Test',
            'code': 'DA',
            'user_type_id': self.user_type_revenue_id,
            })
        invoice_id = self.env['account.invoice'].create({
            'name': 'Discount Invoice Test',
            'partner_id': self.partner_id.id,
            'currency_id': self.env.ref('base.USD').id,
            'account_id': self.account_id.id,
            'type': 'out_invoice',
            'discount_method': 'per',
            'discount_per': 10,
            'date_invoice': time.strftime('%Y') + '-03-12',
            'journal_id': self.journal_id.id,
        })
        self.env['account.invoice.line'].create({
            'product_id': self.env.ref("product.product_product_10").id,
            'quantity': 10,
            'price_unit': 400,
            'discount': 10,
            'invoice_id': invoice_id.id,
            'name': 'Mouse, Optical',
            'account_id': self.account_id.id,
        })
        self.env['account.invoice.line'].create({
            'product_id': self.env.ref("product.product_product_12").id,
            'quantity': 30,
            'price_unit': 250,
            'discount': 10,
            'invoice_id': invoice_id.id,
            'name': 'Mouse, Wireless',
            'account_id': self.account_id.id,
        })
        return invoice_id
