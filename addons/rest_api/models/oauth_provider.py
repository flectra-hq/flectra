# -*- coding: utf-8 -*-
# Author: Ivan Yelizariev, Ildar
# Ref. from: https://github.com/it-projects-llc/odoo-saas-tools/blob/10.0/oauth_provider/models/oauth_provider.py

from flectra import models, fields, api
from datetime import datetime, timedelta
from flectra.tools import DEFAULT_SERVER_DATETIME_FORMAT

try:
    from oauthlib import common as oauthlib_common
except:
    pass


class OauthAccessToken(models.Model):
    _name = 'oauth.access_token'

    token = fields.Char('Access Token', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    expires = fields.Datetime('Expires', required=True)
    scope = fields.Char('Scope')

    @api.multi
    def _get_access_token(self, user_id=None, create=False):
        if not user_id:
            user_id = self.env.user.id

        access_token = self.env['oauth.access_token'].sudo().search(
            [('user_id', '=', user_id)], order='id DESC', limit=1)
        if access_token:
            access_token = access_token[0]
            if access_token.is_expired():
                access_token = None
        if not access_token and create:
            expires = datetime.now() + timedelta(seconds=int(self.env.ref('rest_api.oauth2_access_token_expires_in').sudo().value))
            vals = {
                'user_id': user_id,
                'scope': 'userinfo',
                'expires': expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'token': oauthlib_common.generate_token(),
            }
            access_token = self.env['oauth.access_token'].sudo().create(vals)
            # we have to commit now, because /oauth2/tokeninfo could
            # be called before we finish current transaction.
            self._cr.commit()
        if not access_token:
            return None
        return access_token.token

    @api.multi
    def is_valid(self, scopes=None):
        """
        Checks if the access token is valid.

        :param scopes: An iterable containing the scopes to check or None
        """
        self.ensure_one()
        return not self.is_expired() and self._allow_scopes(scopes)

    @api.multi
    def is_expired(self):
        self.ensure_one()
        return datetime.now() > fields.Datetime.from_string(self.expires)

    @api.multi
    def _allow_scopes(self, scopes):
        self.ensure_one()
        if not scopes:
            return True

        provided_scopes = set(self.scope.split())
        resource_scopes = set(scopes)

        return resource_scopes.issubset(provided_scopes)


class Users(models.Model):
    _inherit = 'res.users'
    token_ids = fields.One2many('oauth.access_token', 'user_id',
                                string="Access Tokens")