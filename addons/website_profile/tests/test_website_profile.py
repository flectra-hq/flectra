# Part of Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests
from flectra.addons.gamification.tests.common import HttpCaseGamification


@flectra.tests.tagged('post_install', '-at_install')
class TestWebsiteProfile(HttpCaseGamification):
    def test_save_change_description(self):
        self.start_tour("/", 'website_profile_description', login="admin")
