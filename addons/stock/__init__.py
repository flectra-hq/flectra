# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from . import controllers
from . import models
from . import report
from . import wizard


from flectra import api, SUPERUSER_ID


# TODO: Apply proper fix & remove in master
def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ir.model.data'].search([
        ('model', 'like', '%stock%'),
        ('module', '=', 'stock')
    ]).unlink()
