# -*- coding: utf-8 -*-

from flectra import fields, models


# defined for access rules
class Product(models.Model):
    _inherit = 'product.product'

    event_ticket_ids = fields.One2many('event.event.ticket', 'product_id', string='Event Tickets')
