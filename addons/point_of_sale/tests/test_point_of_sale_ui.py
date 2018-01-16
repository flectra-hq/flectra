# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests


@flectra.tests.common.at_install(False)
@flectra.tests.common.post_install(True)
class TestUi(flectra.tests.HttpCase):

    def test_01_point_of_sale_tour(self):
        self.phantom_js("/web", "flectra.__DEBUG__.services['web_tour.tour'].run('point_of_sale_tour')", "flectra.__DEBUG__.services['web_tour.tour'].tours.point_of_sale_tour.ready", login="admin")
