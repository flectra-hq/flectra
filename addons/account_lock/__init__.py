# -*- coding: utf-8 -*-

from . import models
from flectra.exceptions import UserError


def uninstall_hook(env):
    if not env.ref('base.module_base').demo:
        raise UserError("This module cannot be uninstalled.")
