# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import http
from flectra.addons.web.controllers.home import Home as WebHome
from flectra.addons.web.controllers.utils import is_user_internal
from flectra.http import request


class Home(WebHome):

    @http.route()
    def index(self, *args, **kw):
        if request.session.uid and not is_user_internal(request.session.uid):
            return request.redirect_query('/my', query=request.params)
        return super().index(*args, **kw)

    def _login_redirect(self, uid, redirect=None):
        if not redirect and not is_user_internal(uid):
            redirect = '/my'
        return super()._login_redirect(uid, redirect=redirect)

    @http.route()
    def web_client(self, s_action=None, **kw):
        if request.session.uid and not is_user_internal(request.session.uid):
            return request.redirect_query('/my', query=request.params)
        return super().web_client(s_action, **kw)
