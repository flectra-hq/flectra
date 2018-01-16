# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests


@flectra.tests.common.at_install(False)
@flectra.tests.common.post_install(True)
class TestUi(flectra.tests.HttpCase):
    
    def test_01_main_flow_tour(self):
        self.phantom_js("/web", "flectra.__DEBUG__.services['web_tour.tour'].run('main_flow_tour')", "flectra.__DEBUG__.services['web_tour.tour'].tours.main_flow_tour.ready", login="admin", timeout=180)
