# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.
from unittest.mock import patch

import flectra.tests
from flectra.addons.pos_self_order.tests.self_order_common_test import SelfOrderCommonTest
# from flectra.addons.pos_online_payment.models.pos_payment_method import PosPaymentMethod


@flectra.tests.tagged("post_install", "-at_install")
class TestSelfOrderFrontendMobile(SelfOrderCommonTest):
    pass
