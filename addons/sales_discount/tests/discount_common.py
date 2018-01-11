# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase


class TestDiscountCommon(TransactionCase):
    def setUp(self):
        super(TestDiscountCommon, self).setUp()
        self.config = self.env['res.config.settings'].create({
            'global_discount_per_so_invoice_line': True,
            'global_discount_apply': True,
            'global_discount_fix_amount': 5000,
            'global_discount_percentage': 50,
        })
        self.config.onchange_global_discount_per_so_invoice_line()
        self.config.onchange_global_discount_apply()
        self.config.set_values()
        self.disc_config_1 = self.env['sale.discount.config'].create({
            'group_id': self.env.ref('sales_team.group_sale_manager').id,
            'fix_amount': 3000.0,
            'percentage': 20.0,
        })
        self.partner_id = self.env.ref('base.res_partner_3')
        self.partner_invoice_id = self.env.ref('base.res_partner_address_11')
        self.user_id = self.env.ref('base.user_root')
        self.partner_shipping_id = self.env.ref('base.res_partner_address_11')
        self.pricelist_id = self.env.ref('product.list0')
        self.product_1 = self.env.ref('product.product_delivery_01')
        self.product_uom = self.env.ref('product.product_uom_unit')
        self.product_2 = self.env.ref('product.product_product_25')
