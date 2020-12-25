# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests


@flectra.tests.tagged('post_install','-at_install')
class TestUi(flectra.tests.HttpCase):

    def test_01_crm_tour(self):
        self.start_tour("/web", 'crm_tour', login="admin")

    def test_02_crm_tour_rainbowman(self):
        # we create a new user to make sure he gets the 'Congrats on your first deal!'
        # rainbowman message.
        self.env['res.users'].create({
            'name': 'Temporary CRM User',
            'login': 'temp_crm_user',
            'password': 'temp_crm_user',
            'groups_id': [(6, 0, [
                    self.ref('base.group_user'),
                    self.ref('sales_team.group_sale_salesman')
                ])]
        })
        self.start_tour("/web", 'crm_rainbowman', login="temp_crm_user")
