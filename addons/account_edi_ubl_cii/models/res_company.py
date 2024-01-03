# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    invoice_is_ubl_cii = fields.Boolean('Generate Peppol format by default', default=False)
