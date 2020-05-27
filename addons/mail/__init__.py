# -*- coding: utf-8 -*-

from . import models
from . import wizard
from . import controllers
from .tests import test_mail_model


def post_init(cr, registry):
    from flectra import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    env['publisher_warranty.contract'].update_notification()
