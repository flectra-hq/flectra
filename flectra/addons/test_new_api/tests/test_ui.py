import flectra.tests

class TestUi(flectra.tests.HttpCase):
    post_install = True
    at_install = False

    def test_01_admin_widget_x2many(self):
        self.phantom_js("/web#action=test_new_api.action_discussions",
                        "flectra.__DEBUG__.services['web_tour.tour'].run('widget_x2many', 100)",
                        "flectra.__DEBUG__.services['web_tour.tour'].tours.widget_x2many.ready",
                        login="admin", timeout=120)
