# -*- coding: utf-8 -*-
# Part of flectra. See LICENSE file for full copyright and licensing details.

from flectra import http
from flectra.http import request
from flectra.addons.website_sale.controllers.main import WebsiteSale
from flectra.addons.portal.controllers.portal import _build_url_w_params
from flectra.tools.misc import formatLang


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/pricelist'], type='http', auth="public", website=True)
    def pricelist(self, promo, **post):
        redirect = post.get('r', '/shop/cart')
        if request.website.pricelist_id.pricelist_type == 'basic':
            return super(WebsiteSale, self).pricelist(promo)
        else:
            sale_order_id = request.session.get('sale_order_id')
            sale_order = request.env['sale.order'].sudo().browse(
                sale_order_id).exists() if sale_order_id else None
            pricelist_id = request.website.pricelist_id
            if pricelist_id and not pricelist_id.apply_coupon_code:
                return request.redirect("%s?apply_coupon_code=1" % redirect)
            coupon_obj = request.env['coupon.code']
            coupon_code_id = coupon_obj.sudo().get_coupon_records(
                promo, request.website.pricelist_id)
            params = {}
            if not coupon_code_id:
                return request.redirect("%s?coupon_code_id=1" % redirect)
            if coupon_code_id.usage_limit > 0 \
                    and coupon_code_id.remaining_limit <= 0:
                return request.redirect("%s?coupon_exceeds_limit=1" % redirect)
            min_order_amount = coupon_code_id.min_order_amount
            if not sale_order.coupon_code_id and min_order_amount \
                    and sale_order.amount_untaxed < min_order_amount:
                params['min_order_amount'] = \
                    formatLang(request.env, min_order_amount,
                               currency_obj=pricelist_id.currency_id)
                params['subtotal'] = \
                    formatLang(request.env, sale_order.amount_untaxed,
                               currency_obj=pricelist_id.currency_id)
                return request.redirect(_build_url_w_params(
                    "%s?coupon_min_order=1" % redirect, params))
            if coupon_code_id.model_id:
                partner_id = request.website.user_id.sudo().partner_id
                check_coupon = coupon_obj.check_condition(
                    coupon_code_id, partner_id)
                if check_coupon:
                    return request.redirect("%s?coupon_condition=1" % redirect)
            check_coupon = True
            for line in sale_order.order_line:
                if line.product_uom_qty < \
                                coupon_code_id.number_of_x_product and not \
                                line.coupon_code_id and check_coupon:
                    check_coupon = True
                else:
                    check_coupon = False
                    break
            if check_coupon:
                return request.redirect("%s?coupon_condition=1" % redirect)
            sale_order.have_coupon_code = promo
            sale_order.apply_coupon_code()
        return request.redirect(redirect)

    @http.route(['/website/discount'], type='http',
                auth="public", website=True)
    def website_discount(self, access_token=None, revive='', **post):
        values = {}
        order = request.website.sale_get_order()
        data = order._get_discount_vals()
        values.update({
            'website_sale_order': order,
            'data': data[0],
            })
        return request.render(
            "website_sale_advance_pricelist.discount_popover", values,
            headers={'Cache-Control': 'no-cache'})
