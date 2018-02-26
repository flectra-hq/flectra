# -*- coding: utf-8 -*-

from flectra import models, fields


class LinkTracker(models.Model):
    _inherit = "link.tracker"

    website_id = fields.Many2one('website', string='Website',
                                 help='Define website in which this '
                                      'link will enabled!')
