# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests


@flectra.tests.tagged('post_install', '-at_install')
class TestUi(flectra.tests.HttpCase):

    def test_01_account_tour(self):
        # This tour doesn't work with demo data on runbot
        all_moves = self.env['account.move'].search([('move_type', '!=', 'entry')])
        all_moves.button_draft()
        all_moves.posted_before = False
        all_moves.unlink()
        self.start_tour("/web", 'account_tour', login="admin")
