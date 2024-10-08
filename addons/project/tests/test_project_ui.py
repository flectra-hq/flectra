# Part of Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests


@flectra.tests.tagged('post_install', '-at_install')
class TestUi(flectra.tests.HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['res.config.settings'].create({'group_project_milestone': True}).execute()

    def test_01_project_tour(self):
        self.start_tour("/web", 'project_tour', login="admin")
