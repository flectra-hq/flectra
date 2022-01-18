# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import flectra
import flectra.tests


@flectra.tests.common.tagged('post_install', '-at_install', 'website_snippets')
class TestSnippets(flectra.tests.HttpCase):

    def test_01_empty_parents_autoremove(self):
        self.start_tour("/?enable_editor=1", "snippet_empty_parent_autoremove", login='admin')

    def test_02_countdown_preview(self):
        self.start_tour("/?enable_editor=1", "snippet_countdown", login='admin')
