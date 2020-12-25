# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import flectra.addons.web.tests.test_js
import flectra.tests


@flectra.tests.tagged("post_install", "-at_install")
class WebSuite(flectra.tests.HttpCase):
    def setUp(self):
        super().setUp()
        env = self.env(user=self.env.ref('base.user_admin'))
        self.main_pos_config = env.ref('point_of_sale.pos_config_main')

    def test_pos_js(self):
        # open a session, the /pos/ui controller will redirect to it
        self.main_pos_config.open_session_cb(check_coa=False)

        # point_of_sale desktop test suite
        self.browser_js(
            "/pos/ui/tests?mod=web&failfast", "", "", login="admin", timeout=1800
        )
