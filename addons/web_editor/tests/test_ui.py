# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests

@flectra.tests.common.at_install(False)
@flectra.tests.common.post_install(True)
class TestUi(flectra.tests.HttpCase):

    post_install = True
    at_install = False

    def test_01_admin_rte(self):
        self.phantom_js("/web", "flectra.__DEBUG__.services['web_tour.tour'].run('rte')", "flectra.__DEBUG__.services['web_tour.tour'].tours.rte.ready", login='admin')

    def test_02_admin_rte_inline(self):
        self.phantom_js("/web", "flectra.__DEBUG__.services['web_tour.tour'].run('rte_inline')", "flectra.__DEBUG__.services['web_tour.tour'].tours.rte_inline.ready", login='admin')
