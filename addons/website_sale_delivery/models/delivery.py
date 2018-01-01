# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class DeliveryCarrier(models.Model):
    _name = 'delivery.carrier'
    _inherit = ['delivery.carrier', 'website.published.mixin']

    website_description = fields.Text(related='product_id.description_sale', string='Description for Online Quotations')
    website_published = fields.Boolean(default=False)
    website_ids = fields.Many2many('website', 'website_del_carrier_pub_rel', 'website_id', 'del_carrier_id', string='Websites', copy=False,
                                   help='List of websites in which Product is published.')
