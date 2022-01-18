# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests


@flectra.tests.tagged('post_install', '-at_install')
class TestWebsiteCrm(flectra.tests.HttpCase):

    def test_tour(self):
        self.start_tour("/", 'website_crm_tour')

        # check result
        record = self.env['crm.lead'].search([('description', '=', '### TOUR DATA ###')])
        self.assertEqual(len(record), 1)
        self.assertEqual(record.contact_name, 'John Smith')
        self.assertEqual(record.email_from, 'john@smith.com')
        self.assertEqual(record.partner_name, 'FlectraHQ, Inc., Odoo S.A.')
