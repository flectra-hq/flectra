# Part of Flectra See LICENSE file for full copyright and licensing details.

from .test_01_sale_order_discount import TestSODiscount
import logging


class TestSODiscountInvoice(TestSODiscount):
    def setUp(self):
        super(TestSODiscountInvoice, self).setUp()

    def test_01_so_dp_fixed_amount(self):
        sale_order = self.discount_01_set_fixamount()
        self.assertTrue(sale_order, 'Sale Order: no sale order created')
        logging.info('Successful: Sale Order Created!')
        sale_order.calculate_discount()
        sale_order.order_line._compute_product_updatable()
        sale_order.action_confirm()
        sale_order.action_invoice_create()

    def test_02_so_percentage_discount(self):
        sale_order = self.discount_02_set_percentages()
        self.assertTrue(sale_order, 'Sale Order: no sale order created')
        logging.info('Successful: Sale Order Created!')
        sale_order.calculate_discount()
        sale_order.order_line._compute_product_updatable()
        sale_order.action_confirm()
        sale_order.action_invoice_create()
