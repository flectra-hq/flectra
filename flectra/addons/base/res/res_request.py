# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


@api.model
def referenceable_models(self):
    return [(link.object, link.name) for link in self.env['res.request.link'].search([])]


class ResRequestLink(models.Model):
    _name = 'res.request.link'
    _order = 'priority'

    name = fields.Char(required=True, translate=True)
    object = fields.Char(required=True)
    priority = fields.Integer(default=5)
