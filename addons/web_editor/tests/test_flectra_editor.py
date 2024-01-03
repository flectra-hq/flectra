# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests

@flectra.tests.tagged("post_install", "-at_install")
class TestFlectraEditor(flectra.tests.HttpCase):

    def test_flectra_editor_suite(self):
        self.browser_js('/web_editor/tests', "", "", login='admin', timeout=1800)
