# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra.addons.website_slides.controllers.main import WebsiteSlides
from flectra.http import request


class WebsiteSaleSlides(WebsiteSlides):

    def _prepare_additional_channel_values(self, values, **kwargs):
        values = super(WebsiteSaleSlides, self)._prepare_additional_channel_values(values, **kwargs)
        channel = values['channel']
        if channel.enroll == 'payment' and channel.product_id:
            pricelist = request.website.get_current_pricelist()
            values['product_info'] = channel.product_id.product_tmpl_id._get_combination_info(product_id=channel.product_id.id, pricelist=pricelist)
            values['product_info']['currency_id'] = request.website.currency_id
        return values
