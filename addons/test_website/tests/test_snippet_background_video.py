# Part of Flectra. See LICENSE file for full copyright and licensing details.

import flectra.tests


@flectra.tests.common.tagged('post_install', '-at_install')
class TestSnippetBackgroundVideo(flectra.tests.HttpCase):

    def test_snippet_background_video(self):
        self.start_tour("/", "snippet_background_video", login="admin")
