# -*- coding: utf-8 -*-
# Part of flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"
    website_id = fields.Many2one('website', 'Website', readonly=True)

    def _select(self):
        return \
            super(SaleReport, self)._select() + ", s.website_id as website_id"

    def _group_by(self):
        res = super(SaleReport, self)._group_by()
        return res + ',s.website_id'
