# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    fiscal_position_id = fields.Many2one('account.fiscal.position',
                                         oldname='fiscal_position',
                                         string='Nature of Transaction')