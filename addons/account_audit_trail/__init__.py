# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from . import models
from flectra.exceptions import UserError


def uninstall_hook(env):
    if not env.ref('base.module_base').demo:
        raise UserError("This module cannot be uninstalled.")
