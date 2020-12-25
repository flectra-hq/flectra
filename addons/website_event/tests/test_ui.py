# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests
from flectra import tools


@flectra.tests.tagged('post_install', '-at_install')
class TestUi(flectra.tests.HttpCase):
    def test_admin(self):
        self.start_tour("/", 'event', login='admin', step_delay=100)
