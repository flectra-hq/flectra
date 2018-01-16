# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import werkzeug

from flectra import http
from flectra.http import request


class LinkTracker(http.Controller):
    @http.route('/r/<string:code>', type='http', auth='none', website=True)
    def full_url_redirect(self, code, **post):
        country_code = request.session.geoip and request.session.geoip.get('country_code') or False
        request.env['link.tracker.click'].add_click(code, request.httprequest.remote_addr, country_code, stat_id=False)
        redirect_url = request.env['link.tracker'].get_url_from_code(code)
        return werkzeug.utils.redirect(redirect_url or '', 301)
