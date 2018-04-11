# Part of Flectra See LICENSE file for full copyright and licensing details.

from .sale_advance_pricelist_common import TestAdvSalePricelist
from flectra.tools import float_compare


class TestCouponCodeMatchDiscount(TestAdvSalePricelist):
    def setUp(self):
        super(TestCouponCodeMatchDiscount, self).setUp()

    def test_Percentage_coupon_code(self):
        if not self.sale_order_2.coupon_flag:
            self.check_all_coupon_code(self.sale_order_2,
                                       'Get10Peroff', self.pricelist_2)
        self.assertTrue(self.sale_order_2.have_coupon_code != '',
                        'Coupon Code: Please enter the coupon code!')
        self.assertEqual(float_compare(
            self.sale_order_2.order_line[0].discount, 24.90,
            precision_digits=2), 0, 'Discount Line: the discount of first'
                                    'sale order line should be 24.90!')
        self.assertEqual(self.sale_order_2.discount, 3305.48,
                         'Sale Discount: the discount for the '
                         'sale order should be 3305.48!')

    def test_Fixed_coupon_code(self):
        if not self.sale_order_3.coupon_flag:
            self.check_all_coupon_code(self.sale_order_3,
                                       'Get20off', self.pricelist_2)
        self.assertTrue(self.sale_order_3.have_coupon_code != '',
                        'Coupon Code: Please enter the coupon code!')
        self.assertEqual(float_compare(
            self.sale_order_3.order_line[0].discount, 17.16,
            precision_digits=2), 0, 'Discount Line: the discount of first'
                                    'sale order line should be 17.16!')
        self.assertEqual(float_compare(
            self.sale_order_3.order_line[1].discount, 15.58,
            precision_digits=2), 0, 'Discount Line: the discount of second'
                                    'sale order line should be 15.58!')
        self.assertEqual(self.sale_order_3.discount, 2138.16,
                         'Sale Discount: the discount for the '
                         'sale order should be 2138.16!')

        # Remove Coupon Code
        self.sale_order_3.apply_coupon_code()
        coupon_code_id = self.CouponCode.search([
            ('coupon_code', '=', 'Get20off')])
        coupon_code_id.write({'discount_amount': 30})

        self.SaleOrderLine.create({
            'name': self.product_3.name,
            'product_id': self.product_3.id,
            'product_uom_qty': 3,
            'product_uom': self.product_3.uom_id.id,
            'price_unit': self.product_3.list_price,
            'order_id': self.sale_order_3.id,
            })
        self.sale_order_3._check_cart_rules()
        self.check_all_coupon_code(self.sale_order_3,
                                   'Get20off', self.pricelist_2)

    def test_Buy_X_Product_Get_Y_Product_Free_coupon_code(self):
        if not self.sale_order_4.coupon_flag:
            self.check_all_coupon_code(self.sale_order_4,
                                       'BXGYFree', self.pricelist_2)
        self.assertTrue(self.sale_order_4.have_coupon_code != '',
                        'Coupon Code: Please enter the coupon code!')
        self.assertEqual(float_compare(
            self.sale_order_4.order_line[0].discount, 14.90,
            precision_digits=2), 0, 'Discount Line: the discount of first'
                                    'sale order line should be 14.90!')
        self.assertEqual(self.sale_order_4.discount, 1977.98,
                         'Sale Discount: the discount for the'
                         ' sale order should be 1977.98!')
        self.assertTrue(len(self.sale_order_4.order_line) == 4,
                        'Sale: Order Line is missing')
        self.assertEqual(self.sale_order_4.order_line[2].price_unit, 0.0,
                         'Price unit of the line should be 0.0!')
        self.assertEqual(self.sale_order_4.order_line[3].price_unit, 0.0,
                         'Price unit of the line should be 0.0!')

    def test_Buy_X_Product_Get_Y_Other_Product_Free_coupon_code(self):
        if not self.sale_order_5.coupon_flag:
            self.check_all_coupon_code(self.sale_order_5,
                                       'BXGYOtherFree', self.pricelist_2)
        self.assertTrue(self.sale_order_5.have_coupon_code != '',
                        'Coupon Code: Please enter coupon code!')
        self.assertEqual(float_compare(
            self.sale_order_5.order_line[0].discount, 14.90,
            precision_digits=2), 0, 'Discount Line: the discount of first'
                                    'sale order line should be 14.90!')
        self.assertEqual(self.sale_order_5.discount, 1977.98,
                         'Sale Discount: the discount for the '
                         'sale order should be 1977.98!')
        self.assertTrue(len(self.sale_order_5.order_line) == 3,
                        'Sale: Order Line is missing')
        self.assertEqual(self.sale_order_5.order_line[2].price_unit, 0.0,
                         'Price unit of the line should be 0.0!')

    def test_Clubbed_Discount_coupon_code(self):
        if not self.sale_order_6.coupon_flag:
            self.check_all_coupon_code(self.sale_order_6,
                                       'CD15Per', self.pricelist_2)
        self.assertTrue(self.sale_order_6.have_coupon_code != '',
                        'Coupon Code: Please enter coupon code!')
        self.assertEqual(float_compare(
            self.sale_order_6.order_line[0].discount, 29.90,
            precision_digits=2), 0, 'Discount Line: the discount of first'
                                    'sale order line should be 29.90!')
        self.assertEqual(self.sale_order_6.discount, 3969.23,
                         'Sale Discount: the discount for the '
                         'sale order should be 3969.23!')
        self.assertEqual(float_compare(
            self.sale_order_6.order_line[1].discount, 29.90,
            precision_digits=2), 0, 'Discount Line: the discount of first'
                                    'sale order line should be 29.90!')
        self.assertEqual(float_compare(
            self.sale_order_6.amount_total, 9305.78, precision_digits=2),
            0, "Total not correct")

    def test_Buy_X_Product_Get_Percent_Free_coupon_code(self):
        if not self.sale_order_7.coupon_flag:
            self.check_all_coupon_code(self.sale_order_7,
                                       'BXGPercentFree', self.pricelist_2)
        self.assertTrue(self.sale_order_7.have_coupon_code != '',
                        'Coupon Code: Please enter the coupon code!')
        self.assertEqual(float_compare(
            self.sale_order_7.order_line[0].discount, 22.65,
            precision_digits=2), 0, 'Discount Line: the discount of first'
                                    'sale order line should be 22.65!')
        self.assertEqual(float_compare(
            self.sale_order_7.order_line[1].discount, 14.90,
            precision_digits=2), 0, 'Discount Line: the discount of first'
                                    'sale order line should be 14.90!')
        self.assertEqual(self.sale_order_7.discount, 1881.36,
                         'Sale Discount: the discount for the'
                         ' sale order should be 1881.36!')
