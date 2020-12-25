import flectra.tests
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.


@flectra.tests.tagged('post_install', '-at_install')
class TestUi(flectra.tests.HttpCase):

    def test_01_sale_tour(self):
        self.start_tour("/web", 'sale_tour', login="admin", step_delay=100)
