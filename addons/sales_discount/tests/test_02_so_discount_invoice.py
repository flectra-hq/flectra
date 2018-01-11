# Part of Flectra See LICENSE file for full copyright and licensing details.

from .test_01_sale_order_discount import TestSODiscount


class TestSODiscountInvoice(TestSODiscount):
    def setUp(self):
        super(TestSODiscountInvoice, self).setUp()

    def test_01_so_dp_fixed_amount(self):
        so = self.discount_01_set_fixamount()
        so._prepare_invoice()

    def test_02_so_percentage_discount(self):
        so = self.discount_02_set_percentages()
        so._prepare_invoice()

