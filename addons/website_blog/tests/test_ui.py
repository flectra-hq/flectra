# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests
from flectra import tools


@flectra.tests.tagged('post_install', '-at_install')
class TestUi(flectra.tests.HttpCase):
    def test_admin(self):
        self.env['blog.blog'].create({'name': 'Travel'})
        self.env['ir.attachment'].create({
            'public': True,
            'type': 'url',
            'url': '/web/image/123/transparent.png',
            'name': 'transparent.png',
            'mimetype': 'image/png',
        })
        self.start_tour("/", 'blog', login='admin')
