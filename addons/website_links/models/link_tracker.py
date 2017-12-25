# -*- coding: utf-8 -*-

from flectra import models, fields, api, _


class LinkTracker(models.Model):

    _inherit = "link.tracker"

    website_id = fields.Many2one('website', string="Link For Website",
                                 required=True)
