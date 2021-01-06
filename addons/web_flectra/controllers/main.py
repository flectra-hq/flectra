# -*- coding: utf-8 -*-
# Copyright 2016, 2019 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
from flectra.http import Controller, request, route
from werkzeug.utils import redirect



class DasboardBackground(Controller):

    def get_view_ids(self, xml_ids):
        ids = []
        for xml_id in xml_ids:
            if "." in xml_id:
                record_id = request.env.ref(xml_id).id
            else:
                record_id = int(xml_id)
            ids.append(record_id)
        return ids

    @route(['/dashboard'], type='http', auth='user', website=False)
    def dashboard(self, **post):
        image = None
        user = request.env.user
        company = user.company_id
        if company.dashboard_background:
            image = base64.b64decode(company.dashboard_background)

        return request.make_response(
            image, [('Content-Type', 'image')])

    @route(['/web/theme_customize_backend_get'],
           type='json', website=True, auth="public")
    def theme_customize_backend_get(self):
        return request.env['res.users'].sudo().search(
            [('id', '=', request.env.user.id)]).dark_mode

    @route(['/web/theme_customize_backend'],
           type='json', website=True, auth="public")
    def theme_customize_backend(self):
        user = request.env['res.users'].sudo().search(
            [('id', '=', request.env.user.id)])
        bool_val = user.dark_mode
        user.update({
            'dark_mode': False if bool_val else True
        })
        return True
