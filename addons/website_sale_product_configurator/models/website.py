# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class Website(models.Model):
    _inherit = 'website'

    add_to_cart_action = fields.Selection(
        selection_add=[('force_dialog', "Let the user decide (dialog)")],
        ondelete={'force_dialog': 'set default'})
