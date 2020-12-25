# -*- coding: utf-8 -*-
from flectra import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    iap_enrich_info = fields.Text('IAP Enrich Info', help='Stores additional info retrieved from IAP in JSON')
