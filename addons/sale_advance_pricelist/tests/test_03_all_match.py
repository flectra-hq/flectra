# Part of Flectra See LICENSE file for full copyright and licensing details.

from .sale_advance_pricelist_common import TestAdvSalePricelist


class TestAllMatchDiscount(TestAdvSalePricelist):
    def setUp(self):
        super(TestAllMatchDiscount, self).setUp()

    def test_All_Match(self):
        self.assertEqual(self.sale_order_8.order_line[0].discount, 12.50,
                         "Discount of first line should be 12.50!")
        self.assertEqual(self.sale_order_8.order_line[1].discount, 10.50,
                         "Discount of Second line should be 10.50!")
        self.assertEqual(self.sale_order_8.discount, 1482.38,
                         'Sale Discount: the discount for the '
                         'sale order should be 1482.38!')

        # Change discount in rules lines
        self.pricelist_3.rule_ids.rule_lines[0].discount_amount = 5
        self.pricelist_3.rule_ids.rule_lines[1].discount_amount = 7
        self.pricelist_3.rule_ids.rule_lines[2].discount_amount = 9

        # Check again percentage and discount in Sale order
        self.sale_order_8._check_cart_rules()
        self.assertEqual(self.sale_order_8.order_line[0].discount, 14.50,
                         "Discount of first line should be 14.50!")
        self.assertEqual(self.sale_order_8.order_line[1].discount, 12.50,
                         "Discount of second line should be 12.50!")
        self.assertEqual(self.sale_order_8.discount, 1747.88,
                         'Sale Discount: the discount for the '
                         'sale order should be 1747.88!')
