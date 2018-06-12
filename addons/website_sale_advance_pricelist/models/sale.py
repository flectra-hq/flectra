# -*- coding: utf-8 -*-
# Part of flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0,
                     attributes=None, **kwargs):
        res = super(SaleOrder, self)._cart_update(product_id, line_id, add_qty,
                                                  set_qty, **kwargs)
        line = self.env['sale.order.line'].browse(res.get('line_id'))
        if res.get('quantity') <= 0 \
                or line.order_id.pricelist_id.pricelist_type == 'basic':
            return res
        if line.order_id.have_coupon_code and \
                line.coupon_code_id and not line.check_coupon:
            return res
        if line.order_id.pricelist_id.discount_policy == 'with_discount':
            if not line.check_coupon:
                line.discount = 0.0
        line.product_id_change()
        line.order_id._check_cart_rules()
        return res


class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def sale_get_order(self, force_create=False, code=None,
                       update_pricelist=False, force_pricelist=False):
        res = super(Website, self).sale_get_order(
            force_create, code, update_pricelist, force_pricelist)
        if res.have_coupon_code:
            for line in res.order_line:
                if line.coupon_code_id and not line.check_coupon:
                    line.write({'discount': 0.0, 'price_unit': 0.0})
        return res
