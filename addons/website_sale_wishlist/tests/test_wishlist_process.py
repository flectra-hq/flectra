# -*- coding: utf-8 -*-
# Part of Odoo,Flectra. See LICENSE file for full copyright and licensing details.
import flectra.tests


@flectra.tests.common.at_install(False)
@flectra.tests.common.post_install(True)
class TestUi(flectra.tests.HttpCase):
    def test_01_wishlist_tour(self):
        self.phantom_js("/", "flectra.__DEBUG__.services['web_tour.tour'].run('shop_wishlist')", "flectra.__DEBUG__.services['web_tour.tour'].tours.shop_wishlist.ready")
