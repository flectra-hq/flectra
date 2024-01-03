# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from . import controllers
from . import models

from flectra.exceptions import UserError
from flectra.tools import config

from flectra.addons.payment import setup_provider, reset_payment_provider


def pre_init_hook(env):
    if not any(config.get(key) for key in ('init', 'update')):
        raise UserError(
            "This module is deprecated and cannot be installed. "
            "Consider installing the Payment Provider: Mercado Pago module instead.")


def post_init_hook(env):
    setup_provider(env, 'payulatam')


def uninstall_hook(env):
    reset_payment_provider(env, 'payulatam')
