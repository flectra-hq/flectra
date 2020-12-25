import flectra.tests
from flectra.tools import mute_logger


@flectra.tests.common.tagged('post_install', '-at_install')
class TestWebsiteError(flectra.tests.HttpCase):

    @mute_logger('flectra.addons.http_routing.models.ir_http', 'flectra.http')
    def test_01_run_test(self):
        self.start_tour("/test_error_view", 'test_error_website')
