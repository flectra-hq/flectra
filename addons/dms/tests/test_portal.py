# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

import flectra.tests


@flectra.tests.tagged("post_install", "-at_install")
class TestDmsPortal(flectra.tests.HttpCase):
    def test_tour(self):
        self.start_tour(
            "/",
            "flectra.__DEBUG__.services['web_tour.tour'].run('dms_portal_tour')",
            "flectra.__DEBUG__.services['web_tour.tour'].tours.dms_portal_tour.ready",
            login="portal",
        )
