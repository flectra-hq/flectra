# Part of Flectra See LICENSE file for full copyright and licensing details.

from .discount_common import TestDiscountCommon
import logging


class TestSODiscount(TestDiscountCommon):
    def setUp(self):
        super(TestSODiscount, self).setUp()

    def discount_01_set_fixamount(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'partner_invoice_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'pricelist_id': self.pricelist_id.id,
        })
        sale_order.onchange_discount_method()
        self.env['sale.order.line'].create({
            'name': self.product_1.name,
            'product_id': self.product_1.id,
            'product_uom_qty': 20,
            'product_uom': self.product_1.uom_id.id,
            'price_unit': self.product_1.list_price,
            'order_id': sale_order.id,
        })
        self.env['sale.order.line'].create({
            'name': self.product_2.name,
            'product_id': self.product_2.id,
            'product_uom_qty': 20,
            'product_uom': self.product_2.uom_id.id,
            'price_unit': self.product_2.list_price,
            'order_id': sale_order.id,
        })
        sale_order.write({
            'discount_method': 'fixed',
            'discount_amount': 100,
        })
        self.assertTrue(sale_order, 'Sale Order: no sale order created')
        logging.info('Successful: Sale Order Created!')
        sale_order.calculate_discount()
        return sale_order

    def discount_02_set_percentages(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'partner_invoice_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'pricelist_id': self.pricelist_id.id,
        })
        sale_order.onchange_discount_method()
        sale_order.write({
            'discount_method': 'per',
            'discount_per': 10,
        })
        self.env['sale.order.line'].create({
            'name': self.product_1.name,
            'product_id': self.product_1.id,
            'product_uom_qty': 10,
            'product_uom': self.product_1.uom_id.id,
            'price_unit': self.product_1.list_price,
            'order_id': sale_order.id,
            'discount': 10,
        })
        self.env['sale.order.line'].create({
            'name': self.product_2.name,
            'product_id': self.product_2.id,
            'product_uom_qty': 20,
            'product_uom': self.product_2.uom_id.id,
            'price_unit': self.product_2.list_price,
            'order_id': sale_order.id,
            'discount': 10,
        })
        self.assertTrue(sale_order, 'Sale Order: no sale order created')
        logging.info('Successful: Sale Order Created!')
        sale_order.calculate_discount()
        sale_order.write({
            'discount_method': 'per',
            'discount_per': 20.0,
        })
        return sale_order
