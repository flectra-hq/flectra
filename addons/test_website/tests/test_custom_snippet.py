# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests
from flectra.tools import mute_logger


@flectra.tests.common.tagged('post_install', '-at_install')
class TestCustomSnippet(flectra.tests.HttpCase):

    @mute_logger('flectra.addons.http_routing.models.ir_http', 'flectra.http')
    def test_01_run_tour(self):
        self.start_tour(self.env['website'].get_client_action_url('/'), 'test_custom_snippet', login="admin")
