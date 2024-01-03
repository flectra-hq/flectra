# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _mailing_enabled = True
