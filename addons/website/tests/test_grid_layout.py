# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

import base64

import flectra.tests
from flectra.tests.common import HOST
from flectra.tools import config

@flectra.tests.common.tagged('post_install', '-at_install')
class TestWebsiteGridLayout(flectra.tests.HttpCase):

    def test_01_replace_grid_image(self):
        IrAttachment = self.env['ir.attachment']
        base = "http://%s:%s" % (HOST, config['http_port'])
        req = self.opener.get(base + '/web/image/website.s_banner_default_image')
        IrAttachment.create({
            'public': True,
            'name': 's_banner_default_image.jpg',
            'type': 'binary',
            'res_model': 'ir_ui_view',
            'datas': base64.b64encode(req.content),
        })
        self.start_tour(self.env['website'].get_client_action_url('/'), 'website_replace_grid_image', login="admin")

    def test_02_scroll_to_new_grid_item(self):
        self.start_tour(self.env['website'].get_client_action_url('/'), 'scroll_to_new_grid_item', login='admin')
