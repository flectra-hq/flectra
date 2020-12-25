import flectra.tests
from flectra.tools import mute_logger


@flectra.tests.common.tagged('post_install', '-at_install')
class TestWebsiteSession(flectra.tests.HttpCase):

    def test_01_run_test(self):
        self.start_tour('/', 'test_json_auth')
