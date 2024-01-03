# -*- coding: utf-8 -*-

from flectra.http import request
from flectra.addons.portal.controllers.portal import CustomerPortal

class CustomerPortalPasswordPolicy(CustomerPortal):
    def _prepare_portal_layout_values(self):
        d = super()._prepare_portal_layout_values()
        d['password_minimum_length'] = request.env['ir.config_parameter'].sudo().get_param('auth_password_policy.minlength')
        return d
