# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.


import flectra.tests


@flectra.tests.common.at_install(False)
@flectra.tests.common.post_install(True)
class TestUi(flectra.tests.HttpCase):
    def test_01_web_rma(self):
        self.phantom_js("/my/home", "flectra.__DEBUG__.services["
                                    "'web_tour.tour'].run('web_rma')",
                        "flectra.__DEBUG__.services['web_tour.tour'"
                        "].tours.web_rma.ready", login="admin")
