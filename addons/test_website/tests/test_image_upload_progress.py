# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra.addons.web_editor.controllers.main import Web_Editor
from flectra.addons.web_unsplash.controllers.main import Web_Unsplash

import flectra.tests

from flectra import http


@flectra.tests.common.tagged('post_install', '-at_install')
class TestImageUploadProgress(flectra.tests.HttpCase):

    def test_01_image_upload_progress(self):
        self.start_tour(self.env['website'].get_client_action_url('/test_image_progress'), 'test_image_upload_progress', login="admin")

    def test_02_image_upload_progress_unsplash(self):
        BASE_URL = self.base_url()

        @http.route('/web_editor/media_library_search', type='json', auth="user", website=True)
        def media_library_search(self, **params):
            return {"results": 0, "media": []}
        # because not preprocessed by ControllerType metaclass
        media_library_search.original_endpoint.routing_type = 'json'
        # disable undraw, no third party should be called in tests
        self.patch(Web_Editor, 'media_library_search', media_library_search)

        @http.route("/web_unsplash/fetch_images", type='json', auth="user")
        def fetch_unsplash_images(self, **post):
            return {
                'total': 1434,
                'total_pages': 48,
                'results': [{
                    'id': 'HQqIOc8oYro',
                    'alt_description': 'brown fox sitting on green grass field during daytime',
                    'urls': {
                        # 'regular': 'https://images.unsplash.com/photo-1462953491269-9aff00919695?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=MnwzMDUwOHwwfDF8c2VhcmNofDF8fGZveHxlbnwwfHx8fDE2MzEwMzIzNDE&ixlib=rb-1.2.1&q=80&w=1080',
                        'regular': BASE_URL + '/website/static/src/img/phone.png',
                    },
                    'links': {
                        # 'download_location': 'https://api.unsplash.com/photos/HQqIOc8oYro/download?ixid=MnwzMDUwOHwwfDF8c2VhcmNofDF8fGZveHxlbnwwfHx8fDE2MzEwMzIzNDE'
                        'download_location': BASE_URL + '/website/static/src/img/phone.png',
                    },
                    'user': {
                        'name': 'Mitchell Admin',
                        'links': {
                            'html': BASE_URL,
                        },
                    },
                }]
            }
        # because not preprocessed by ControllerType metaclass
        fetch_unsplash_images.original_endpoint.routing_type = 'json'
        # disable undraw, no third party should be called in tests
        self.patch(Web_Unsplash, 'fetch_unsplash_images', fetch_unsplash_images)

        self.start_tour(self.env['website'].get_client_action_url('/test_image_progress'), 'test_image_upload_progress_unsplash', login="admin")
