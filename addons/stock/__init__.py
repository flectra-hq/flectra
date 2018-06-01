# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from . import controllers
from . import models
from . import report
from . import wizard
from flectra import api
from flectra.api import Environment, SUPERUSER_ID


# TODO: Apply proper fix & remove in master
def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ir.model.data'].search([
        ('model', 'like', '%stock%'),
        ('module', '=', 'stock')
    ]).unlink()


def post_init_check(cr, registery):
    env = Environment(cr, SUPERUSER_ID, {})
    move_obj = env['stock.move']
    move_ids = move_obj.search([])
    move_ids.set_move_type()
    done_moves = move_obj.search([('state', '=', 'done')], order='date')
    done_moves.check_move_bal_qty()
    return True
