# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models


class Partner(models.Model):
    _inherit = 'res.partner'
    _mailing_enabled = True
