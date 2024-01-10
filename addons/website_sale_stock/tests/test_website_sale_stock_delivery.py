# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra.tests import tagged

from flectra.addons.payment.tests.common import PaymentCommon
from flectra.addons.sale.tests.common import SaleCommon
from flectra.addons.website.tools import MockRequest
from flectra.addons.website_sale.controllers.delivery import WebsiteSaleDelivery
from flectra.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestWebsiteSaleStockDeliveryController(PaymentCommon, SaleCommon):
    def setUp(self):
        super().setUp()
        self.website = self.env.ref('website.default_website')
        self.Controller = WebsiteSaleDelivery()

    def test_validate_payment_with_no_available_delivery_method(self):
        """
        An error should be raised if you try to validate an order with a storable
        product without any delivery method available
        """
        storable_product = self.env['product.product'].create({
            'name': 'Storable Product',
            'sale_ok': True,
            'type': 'product',
            'website_published': True,
        })
        carriers = self.env['delivery.carrier'].search([])
        carriers.write({'website_published': False})

        with MockRequest(self.env, website=self.website):
            self.website.sale_get_order(force_create=True)
            self.Controller.cart_update_json(product_id=storable_product.id, add_qty=1)
            with self.assertRaises(ValidationError):
                self.Controller.shop_payment_validate()
