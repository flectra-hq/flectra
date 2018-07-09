# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase


class TestAdvSalePricelist(TransactionCase):
    def setUp(self):
        super(TestAdvSalePricelist, self).setUp()
        self.partner_id = self.env.ref(
            'sale_advance_pricelist.res_partner_advance_pricelist')
        self.currency_id = self.env.ref('base.USD')
        self.category_id = self.env.ref('product.product_category_5')

        self.main_company = self.env.ref('base.main_company')
        self.main_company.currency_id = self.env.ref('base.USD').id

        self.pricelist_1 = \
            self.env.ref('sale_advance_pricelist.advance_pricelist')
        self.pricelist_2 = self.env.ref(
            'sale_advance_pricelist.advance_pricelist_with_coupon')
        self.pricelist_3 = \
            self.env.ref('sale_advance_pricelist.advance_pricelist_all')

        self.sale_order_2 = \
            self.env.ref('sale_advance_pricelist.sale_order_ap_2')
        self.sale_order_3 = \
            self.env.ref('sale_advance_pricelist.sale_order_ap_3')
        self.sale_order_4 = \
            self.env.ref('sale_advance_pricelist.sale_order_ap_4')
        self.sale_order_5 = \
            self.env.ref('sale_advance_pricelist.sale_order_ap_5')
        self.sale_order_6 = \
            self.env.ref('sale_advance_pricelist.sale_order_ap_6')
        self.sale_order_7 = \
            self.env.ref('sale_advance_pricelist.sale_order_ap_7')
        self.sale_order_8 = \
            self.env.ref('sale_advance_pricelist.sale_order_ap_all_1')

        self.product_1 = self.env.ref('product.product_product_24')
        self.product_2 = self.env.ref('product.product_product_25')
        self.product_3 = self.env.ref('product.product_product_16')

        self.SaleOrder = self.env['sale.order']
        self.SaleOrderLine = self.env['sale.order.line']
        self.CouponCode = self.env['coupon.code']

    def check_all_coupon_code(self, order_id, coupon_code, pricelist_id):
        coupon_code_id = self.CouponCode.get_coupon_records(
            coupon_code, pricelist_id)
        self.assertEqual(len(coupon_code_id), 1, 'Coupon code should be 1!')
        order_id.have_coupon_code = coupon_code
        order_id.apply_coupon_code()
