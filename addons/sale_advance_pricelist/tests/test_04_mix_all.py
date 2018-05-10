# Part of Flectra See LICENSE file for full copyright and licensing details.

from .sale_advance_pricelist_common import TestAdvSalePricelist


class TestMixAllDiscount(TestAdvSalePricelist):
    def setUp(self):
        super(TestMixAllDiscount, self).setUp()

    def test_Mix_All_Match(self):
        PriceRule = self.env['price.rule']
        RuleLine = self.env['rule.line']
        ProductPricelis = self.env['product.pricelist']

        self.pricelist_id = ProductPricelis.create({
            'name': 'Test Pricelist',
            'sequence': 4,
            'discount_policy': 'without_discount',
            'pricelist_type': 'advance',
            'currency_id': self.currency_id.id,
            'apply_method': 'all_matched_rules',
            'apply_coupon_code': True,
        })

        price_rule_id = PriceRule.create({
            'sequence': 1,
            'apply_on': 'category',
            'categ_id': self.category_id.id,
            'pricelist_id': self.pricelist_id.id,
        })
        price_rule_id._get_pricerule_name_price()
        price_rule_id._onchange_apply_on()

        rule_line_1 = RuleLine.create({
            'sequence': 1,
            'min_qty': 1,
            'max_qty': 10,
            'rule_type': 'percent',
            'discount_amount': 12.5,
            'price_rule_id': price_rule_id.id,
            'model_id': self.env.ref('base.model_res_partner').id,
        })

        rule_line_1.check_percentage()
        rule_line_1.check_date()

        rule_line_2 = RuleLine.create({
            'sequence': 1,
            'min_qty': 5,
            'max_qty': 20,
            'rule_type': 'percent',
            'discount_amount': 15,
            'price_rule_id': price_rule_id.id,
        })
        rule_line_2._compute_model()

        cart_rule_1 = self.env.ref('sale_advance_pricelist.cart_rule_1').copy()
        cart_rule_1.pricelist_id = self.pricelist_id.id
        cart_rule_1._get_cart_name_price()
        cart_rule_1.check_percentage()

        cart_rule_2 = self.env.ref('sale_advance_pricelist.cart_rule_2').copy()
        cart_rule_2.pricelist_id = self.pricelist_id.id
        cart_rule_2._get_cart_name_price()

        self.coupon_code_id = self.CouponCode.create({
            'name': 'Get 7%',
            'coupon_code': 'GetDiscount',
            'apply_on': 'category',
            'categ_id': self.category_id.id,
            'pricelist_id': self.pricelist_id.id,
            'discount_amount': 7,
            'coupon_type': 'percent',
            'model_id': self.env.ref('base.model_res_partner').id,
        })
        self.coupon_code_id._onchange_apply_on()
        self.coupon_code_id.check_percentage()
        self.coupon_code_id.check_clubbed_percentage()
        self.coupon_code_id._compute_model()
        check_coupon = self.CouponCode.check_condition(
            self.coupon_code_id, self.partner_id)
        self.assertEqual(check_coupon, False,
                         "Coupon code condition criteria not match!")

        # Check for All Match Discount
        sale_order = self.sale_order_2.copy()
        sale_order.pricelist_id = self.pricelist_id.id
        first_order_line = sale_order.order_line[0]
        first_order_line._onchange_discount()
        second_order_line = sale_order.order_line[1]
        second_order_line._onchange_discount()
        sale_order._check_cart_rules()

        self.assertEqual(first_order_line.discount, 34.00,
                         'Discount Percentage: the discount for the'
                         ' first sale order line should be 34!')

        self.assertEqual(second_order_line.discount, 19.00,
                         'Discount Percentage: the discount for the'
                         ' second sale order line should be 19.00!')

        # Check for Smallest Discount
        self.pricelist_id.apply_method = 'smallest_discount'
        tmp_id = self.product_1.product_tmpl_id.id
        price_rule_id.write({'apply_on': 'product_template',
                             'categ_id': False,
                             'product_tmpl_id': tmp_id})
        price_rule_id._get_pricerule_name_price()
        price_rule_id._onchange_apply_on()
        self.sale_order = self.sale_order_2.copy()
        self.sale_order.pricelist_id = self.pricelist_id.id

        first_order_line = self.sale_order.order_line[0]
        first_order_line._onchange_discount()
        self.assertEqual(first_order_line.discount, 19.0,
                         'Discount Percentage: the discount for the'
                         ' sale order line should be 19.0!')

        # Set coupon code with percent
        self.check_all_condition(self.sale_order, 'percent')
        # Set coupon code with fixed_amount
        self.check_all_condition(self.sale_order, 'fixed_amount')
        # Set coupon code with buy_x_get_y
        self.check_all_condition(self.sale_order, 'buy_x_get_y')
        # Set coupon code with buy_x_get_y_other
        self.check_all_condition(self.sale_order, 'buy_x_get_y_other')

        # Check for Biggest Discount
        self.pricelist_id.apply_method = 'biggest_discount'
        price_rule_id.write({'apply_on': 'product',
                             'categ_id': False,
                             'product_tmpl_id': False,
                             'product_id': self.product_1.id})
        price_rule_id._get_pricerule_name_price()
        cart_rule_3 = \
            self.env.ref('sale_advance_pricelist.cart_rule_all_3').copy()
        cart_rule_3.pricelist_id = self.pricelist_id.id
        cart_rule_3._get_cart_name_price()
        self.sale_order_1 = self.sale_order_2.copy()
        self.sale_order_1.pricelist_id = self.pricelist_id.id

        first_order_line = self.sale_order_1.order_line[0]
        first_order_line._onchange_discount()
        self.assertEqual(first_order_line.discount, 21.50,
                         'Discount Percentage: the discount for the'
                         ' first sale order line should be 21.50!')

        self.sale_order_1.coupon_flag = False
        # # Set coupon code with buy_x_get_percent_free
        self.check_all_condition(self.sale_order_1, 'buy_x_get_percent')
        self.assertEqual(first_order_line.discount, 41.50,
                         'Discount Percentage: the discount for the'
                         ' first sale order line should be 41.50!')

    def check_all_condition(self, sale_order, coupon_type):

        self.coupon_code_id.write({'coupon_type': coupon_type,
                                   'apply_on': 'category',
                                   'categ_id': self.category_id.id})
        if coupon_type in ['percent', 'fixed_amount']:
            self.coupon_code_id.write({'discount_amount': 20})
        elif coupon_type == 'buy_x_get_percent':
            self.coupon_code_id.write({'discount_amount': 20,
                                       'number_of_x_product': 3})
        elif coupon_type == 'buy_x_get_y':
            self.coupon_code_id.write({'number_of_x_product': 2,
                                       'number_of_y_product': 1,
                                       'discount_amount': 0.0})
        else:
            self.coupon_code_id.write({'number_of_x_product': 2,
                                       'number_of_y_product': 1,
                                       'discount_amount': 0.0,
                                       'other_product_id': self.product_3.id})
        self.coupon_code_id.check_percentage()
        # Category Coupon Code
        self.check_all_coupon_code(sale_order,
                                   'GetDiscount', self.pricelist_id)

        # Product Coupon Code
        self.coupon_code_id.write({'apply_on': 'product',
                                   'product_id': self.product_1.id})
        self.check_all_coupon_code(sale_order,
                                   'GetDiscount', self.pricelist_id)

        # Product Template Coupon Code
        template_id = self.product_1.product_tmpl_id.id
        self.coupon_code_id.write({'apply_on': 'product_template',
                                   'product_tmpl_id': template_id})
        self.check_all_coupon_code(sale_order,
                                   'GetDiscount', self.pricelist_id)
