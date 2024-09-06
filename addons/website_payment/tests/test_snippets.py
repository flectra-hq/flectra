import flectra
import flectra.tests


@flectra.tests.common.tagged('post_install', '-at_install')
class TestSnippets(flectra.tests.HttpCase):

    def test_01_donation(self):
        demo_provider = self.env['payment.provider'].search([('code', '=', "demo")])
        demo_provider.write({'state': 'test'})

        self.start_tour("/?enable_editor=1", "donation_snippet_edition", login='admin')
