# Part of Flectra See LICENSE file for full copyright and licensing details.

from .sale_advance_pricelist_common import TestAdvSalePricelist
from flectra.tools import float_compare


class TestFirstMatchDiscount(TestAdvSalePricelist):
    def setUp(self):
        super(TestFirstMatchDiscount, self).setUp()

    def test_discount_rule_and_cart(self):
        so = self.SaleOrder.create({
            'partner_id': self.partner_id.id,
            'partner_invoice_id': self.partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'pricelist_id': self.pricelist_1.id,
        })
        line_1 = self.SaleOrderLine.create({
            'name': self.product_1.name,
            'product_id': self.product_1.id,
            'product_uom_qty': 5,
            'product_uom': self.product_1.uom_id.id,
            'price_unit': self.product_1.list_price,
            'order_id': so.id,
            })
        self.SaleOrderLine.create({
            'name': self.product_2.name,
            'product_id': self.product_2.id,
            'product_uom_qty': 3,
            'product_uom': self.product_2.uom_id.id,
            'price_unit': self.product_2.list_price,
            'order_id': so.id,
            })

        self.SaleOrderLine.create({
            'name': self.product_3.name,
            'product_id': self.product_3.id,
            'product_uom_qty': 3,
            'product_uom': self.product_3.uom_id.id,
            'price_unit': self.product_3.list_price,
            'order_id': so.id,
            })

        so._check_cart_rules()
        so._get_discount_info_JSON()
        self.assertEqual(float_compare(
            so.order_line[0].discount, 12.15,
            precision_digits=2), 0, 'Discount Line: the discount of first'
                                    'sale order line should be 12.15!')

        line_1.write({'price_unit': 1200})
        so._check_cart_rules()
        self.assertEqual(float_compare(
            so.order_line[0].discount, 10.67,
            precision_digits=2), 0, 'Discount Line: the discount of first'
                                    'sale order line should be 10.67!')

        self.assertEqual(float_compare(
            so.order_line[1].discount, 8.19,
            precision_digits=2), 0, 'Discount Line: the discount of second'
                                    'sale order line should be 8.19!')

        line_1.write({'price_unit': 885})
        so._check_cart_rules()
        self.assertEqual(so.discount, 1337.45,
                         'Sale Discount: the discount for the '
                         'sale order should be 1337.45!')

        # Change discount policy
        so.pricelist_id.discount_policy = 'with_discount'
        line_1.write({'product_uom_qty': 1})
        line_1._onchange_discount()
        so._check_cart_rules()
        self.assertEqual(line_1.price_unit, 777.48,
                         "Price unit of the line should be 777.48!")
        self.assertEqual(line_1.discount, 0.0,
                         "Price unit of the line should be 0.0!")

        self.assertEqual(float_compare(
            so.order_line[0].discount, 00.00,
            precision_digits=2), 0, 'Discount Line: the discount of first'
                                    'sale order line should be 00.00!')

        basic_pricelist = self.env['product.pricelist'].create({
            'name': 'Basic Pricelist',
            'sequence': 1,
            'discount_policy': 'without_discount',
            'pricelist_type': 'basic',
            'currency_id': self.currency_id.id,
            'item_ids': [(0, 0, {'compute_price': 'percentage',
                                 'percent_price': 10})],
        })
        so_1 = so.copy()
        so_1.pricelist_id = basic_pricelist.id
        self.assertEqual(float_compare(
            so.order_line[0].discount, 00.00,
            precision_digits=2), 0, 'Discount Line: the discount of first'
                                    'sale order line should be 00.00!')
        so_1.order_line[0]._onchange_discount()
        so_1._get_discount_vals()
        self.assertEqual(float_compare(
            so_1.order_line[0].discount, 10.00,
            precision_digits=2), 0, 'Discount Line: the discount of first'
                                    'sale order line should be 10.00!')
