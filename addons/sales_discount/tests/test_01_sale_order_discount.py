# Part of Flectra See LICENSE file for full copyright and licensing details.

from .discount_common import TestDiscountCommon


class TestSODiscount(TestDiscountCommon):
    def setUp(self):
        super(TestSODiscount, self).setUp()

    def discount_01_set_fixamount(self):
        self.sale_order.onchange_discount_method()
        self.SaleOrderLine.create({
            'name': self.product_1.name,
            'product_id': self.product_1.id,
            'product_uom_qty': 20,
            'product_uom': self.product_1.uom_id.id,
            'price_unit': self.product_1.list_price,
            'order_id': self.sale_order.id,
        })
        self.SaleOrderLine.create({
            'name': self.product_2.name,
            'product_id': self.product_2.id,
            'product_uom_qty': 20,
            'product_uom': self.product_2.uom_id.id,
            'price_unit': self.product_2.list_price,
            'order_id': self.sale_order.id,
        })
        self.sale_order.write({
            'discount_method': 'fixed',
            'discount_amount': 100,
        })
        return self.sale_order

    def discount_02_set_percentages(self):
        self.sale_order.onchange_discount_method()
        self.sale_order.write({
            'discount_method': 'per',
            'discount_per': 10,
        })
        self.SaleOrderLine.create({
            'name': self.product_1.name,
            'product_id': self.product_1.id,
            'product_uom_qty': 10,
            'product_uom': self.product_1.uom_id.id,
            'price_unit': self.product_1.list_price,
            'order_id': self.sale_order.id,
            'discount': 10,
        })
        self.SaleOrderLine.create({
            'name': self.product_2.name,
            'product_id': self.product_2.id,
            'product_uom_qty': 20,
            'product_uom': self.product_2.uom_id.id,
            'price_unit': self.product_2.list_price,
            'order_id': self.sale_order.id,
            'discount': 10,
        })
        self.sale_order.write({
            'discount_method': 'per',
            'discount_per': 20.0,
        })
        return self.sale_order

    def discount_03_check_include_taxes(self):
        self.sale_order.onchange_discount_method()

        tax_id = self.env['account.tax'].create({
            'name': 'Tax 7.7',
            'amount': 7.7,
            'amount_type': 'percent',
            'price_include': True,
            'include_base_amount': True,
        })

        self.SaleOrderLine.create({
            'name': self.product_1.name,
            'product_id': self.product_1.id,
            'product_uom_qty': 1,
            'product_uom': self.product_1.uom_id.id,
            'price_unit': 100,
            'tax_id': [(6, 0, [tax_id.id])],
            'order_id': self.sale_order.id,
        })
        self.SaleOrderLine.create({
            'name': self.product_2.name,
            'product_id': self.product_2.id,
            'product_uom_qty': 1,
            'product_uom': self.product_2.uom_id.id,
            'price_unit': 200,
            'tax_id': [(6, 0, [tax_id.id])],
            'order_id': self.sale_order.id,
        })

        self.sale_order.write({
            'discount_method': 'fixed',
            'discount_amount': 10,
        })
        return self.sale_order
