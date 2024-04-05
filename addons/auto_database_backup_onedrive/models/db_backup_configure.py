# Part of Flectra. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################

import datetime
import json
import logging
import tempfile
from datetime import timedelta

import requests
from werkzeug import urls

import flectra
from flectra import api, fields, models
from flectra.http import request

_logger = logging.getLogger(__name__)

ONEDRIVE_SCOPE = ['offline_access openid Files.ReadWrite.All']
MICROSOFT_GRAPH_END_POINT = "https://graph.microsoft.com"


class AutoDatabaseBackup(models.Model):
    _inherit = 'db.backup.configure'
    _description = 'Automatic Database Backup'

    backup_destination = fields.Selection(selection_add=[('onedrive', 'Onedrive')],
                                          ondelete={'onedrive': 'set default'})

    onedrive_client_id = fields.Char(string='Onedrive Client ID', copy=False)
    onedrive_client_secret = fields.Char(string='Onedrive Client Secret', copy=False)
    onedrive_access_token = fields.Char(string='Onedrive Access Token', copy=False)
    onedrive_refresh_token = fields.Char(string='Onedrive Refresh Token', copy=False)
    onedrive_token_validity = fields.Datetime(string='Onedrive Token Validity',
                                              copy=False)
    onedrive_folder = fields.Char(string='Folder Name')
    onedrive_folder_id = fields.Char(string='Folder ID')
    is_onedrive_token_generated =\
        fields.Boolean(string='onedrive Tokens Generated',
                       compute='_compute_is_onedrive_token_generated', copy=False)
    onedrive_redirect_uri = fields.Char(string='Onedrive Redirect URI',
                                        compute='_compute_odrive_redirect_uri')

    def _compute_odrive_redirect_uri(self):
        for rec in self:
            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
            rec.onedrive_redirect_uri = base_url + '/onedrive/authentication'

    @api.depends('onedrive_access_token', 'onedrive_refresh_token')
    def _compute_is_onedrive_token_generated(self):
        """
        Set true if onedrive tokens are generated
        """
        for rec in self:
            rec.is_onedrive_token_generated =\
                bool(rec.onedrive_access_token) and bool(rec.onedrive_refresh_token)

    def action_get_onedrive_auth_code(self):
        """
        Generate onedrive authorization code
        """
        AUTHORITY = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
        action = self.env["ir.actions.act_window"].sudo()._for_xml_id(
            "auto_database_backup.action_db_backup_configure")
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        url_return = base_url + '/web#id=%d&action=%d&view_type=form&model=%s' % (self.id, action['id'], 'db.backup.configure') # noqa
        state = {
            'backup_config_id': self.id,
            'url_return': url_return
        }
        encoded_params = urls.url_encode({
            'response_type': 'code',
            'client_id': self.onedrive_client_id,
            'state': json.dumps(state),
            'scope': ONEDRIVE_SCOPE,
            'redirect_uri': base_url + '/onedrive/authentication',
            'prompt': 'consent',
            'access_type': 'offline'
        })
        auth_url = "%s?%s" % (AUTHORITY, encoded_params)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': auth_url,
        }

    def generate_onedrive_refresh_token(self):
        """
        generate onedrive access token from refresh token if expired
        """
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        data = {
            'client_id': self.onedrive_client_id,
            'client_secret': self.onedrive_client_secret,
            'scope': ONEDRIVE_SCOPE,
            'grant_type': "refresh_token",
            'redirect_uri': base_url + '/onedrive/authentication',
            'refresh_token': self.onedrive_refresh_token
        }
        try:
            res = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token", data=data, headers=headers) # noqa
            res.raise_for_status()
            response = res.content and res.json() or {}
            if response:
                expires_in = response.get('expires_in')
                self.write({
                    'onedrive_access_token': response.get('access_token'),
                    'onedrive_refresh_token': response.get('refresh_token'),
                    'onedrive_token_validity': fields.Datetime.now() + timedelta(
                        seconds=expires_in) if expires_in else False,
                })
        except requests.HTTPError as error:
            _logger.exception("Bad microsoft onedrive request : %s !",
                              error.response.content)
            raise error

    def get_onedrive_tokens(self, authorize_code):
        """
        Generate onedrive tokens from authorization code
        """
        headers = {"content-type": "application/x-www-form-urlencoded"}
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        data = {
            'code': authorize_code,
            'client_id': self.onedrive_client_id,
            'client_secret': self.onedrive_client_secret,
            'grant_type': 'authorization_code',
            'scope': ONEDRIVE_SCOPE,
            'redirect_uri': base_url + '/onedrive/authentication'
        }
        try:
            res = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token", data=data, headers=headers) # noqa
            res.raise_for_status()
            response = res.content and res.json() or {}
            if response:
                expires_in = response.get('expires_in')
                self.write({
                    'onedrive_access_token': response.get('access_token'),
                    'onedrive_refresh_token': response.get('refresh_token'),
                    'onedrive_token_validity': fields.Datetime.now() + timedelta(
                        seconds=expires_in) if expires_in else False,
                })
        except requests.HTTPError as error:
            _logger.exception("Bad microsoft onedrive request : %s !",
                              error.response.content)
            raise error

    def backup_to_onedrive(self, rec):
        mail_template_success = self.env.ref('auto_database_backup.'
                                             'mail_template_data_db_backup_successful')
        mail_template_failed = self.env.ref('auto_database_backup.'
                                            'mail_template_data_db_backup_failed')
        backup_time = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = "%s_%s.%s" % (rec.db_name, backup_time, rec.backup_format)

        if rec.onedrive_token_validity <= fields.Datetime.now():
            rec.generate_onedrive_refresh_token()
        temp = tempfile.NamedTemporaryFile(suffix='.%s' % rec.backup_format)
        with open(temp.name, "wb+") as tmp:
            flectra.service.db.dump_db(rec.db_name, tmp, rec.backup_format)
        headers = {
            'Authorization': 'Bearer {}'.format(rec.onedrive_access_token),
            'Content-Type': 'application/json'
        }
        upload_session_url = MICROSOFT_GRAPH_END_POINT + "/v1.0/me/drive/root:/%s/%s:/createUploadSession" % (rec.onedrive_folder, backup_filename) # noqa
        try:
            upload_session = requests.post(upload_session_url, headers=headers)
            upload_url = upload_session.json().get('uploadUrl')
            requests.put(upload_url, data=temp.read())
            if rec.auto_remove:
                list_url = MICROSOFT_GRAPH_END_POINT + "/v1.0/me/drive/items/%s/children" % rec.onedrive_folder_id # noqa
                response = requests.get(list_url, headers=headers)
                files = response.json().get('value')
                for file in files:
                    create_time = file['createdDateTime'][:19].replace('T', ' ')
                    diff_days = (datetime.datetime.now() - datetime.datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')).days # noqa
                    if diff_days >= rec.days_to_remove:
                        delete_url = MICROSOFT_GRAPH_END_POINT + "/v1.0/me/drive/items/%s" % file['id'] # noqa
                        requests.delete(delete_url, headers=headers)
            if rec.notify_user:
                mail_template_success.send_mail(rec.id, force_send=True)
        except Exception as error:
            rec.generated_exception = error
            _logger.info('Onedrive Exception: %s', error)
            if rec.notify_user:
                mail_template_failed.send_mail(rec.id, force_send=True)
