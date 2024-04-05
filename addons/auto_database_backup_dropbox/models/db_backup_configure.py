# Part of Flectra. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################

import datetime
import logging
import tempfile

import dropbox

import flectra
from flectra import api, fields, models

_logger = logging.getLogger(__name__)


class AutoDatabaseBackup(models.Model):
    _inherit = 'db.backup.configure'
    _description = 'Automatic Database Backup'

    backup_destination = fields.Selection(selection_add=[('dropbox', 'Dropbox')],
                                          ondelete={'dropbox': 'set default'})

    dropbox_client_id = fields.Char(string='Dropbox Client ID', copy=False)
    dropbox_client_secret = fields.Char(string='Dropbox Client Secret', copy=False)
    dropbox_refresh_token = fields.Char(string='Dropbox Refresh Token', copy=False)
    is_dropbox_token_generated =\
        fields.Boolean(string='Dropbox Token Generated',
                       compute='_compute_is_dropbox_token_generated', copy=False)
    dropbox_folder = fields.Char('Dropbox Folder')

    @api.depends('dropbox_refresh_token')
    def _compute_is_dropbox_token_generated(self):
        """
        Set True if the dropbox refresh token is generated
        """
        for rec in self:
            rec.is_dropbox_token_generated = bool(rec.dropbox_refresh_token)

    def action_get_dropbox_auth_code(self):
        """
        Open a wizard to set up dropbox Authorization code
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dropbox Authorization Wizard',
            'res_model': 'authentication.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'dropbox_auth': True}
        }

    def get_dropbox_auth_url(self):
        """
        Return dropbox authorization url
        """
        dbx_auth =\
            dropbox.oauth.DropboxOAuth2FlowNoRedirect(self.dropbox_client_id,
                                                      self.dropbox_client_secret,
                                                      token_access_type='offline')
        auth_url = dbx_auth.start()
        return auth_url

    def set_dropbox_refresh_token(self, auth_code):
        """
        Generate and set the dropbox refresh token from authorization code
        """
        dbx_auth =\
            dropbox.oauth.DropboxOAuth2FlowNoRedirect(self.dropbox_client_id,
                                                      self.dropbox_client_secret,
                                                      token_access_type='offline')
        outh_result = dbx_auth.finish(auth_code)
        self.dropbox_refresh_token = outh_result.refresh_token

    def backup_to_dropbox(self, rec):
        mail_template_success = self.env.ref('auto_database_backup.'
                                             'mail_template_data_db_backup_successful')
        mail_template_failed = self.env.ref('auto_database_backup.'
                                            'mail_template_data_db_backup_failed')
        backup_time = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = "%s_%s.%s" % (rec.db_name, backup_time, rec.backup_format)

        temp = tempfile.NamedTemporaryFile(suffix='.%s' % rec.backup_format)
        with open(temp.name, "wb+") as tmp:
            flectra.service.db.dump_db(rec.db_name, tmp, rec.backup_format)
        try:
            dbx = dropbox.Dropbox(app_key=rec.dropbox_client_id,
                                  app_secret=rec.dropbox_client_secret,
                                  oauth2_refresh_token=rec.dropbox_refresh_token)
            dropbox_destination = '/' + rec.dropbox_folder + '/' + backup_filename
            dbx.files_upload(temp.read(), dropbox_destination)
            if rec.auto_remove:
                files = dbx.files_list_folder(rec.dropbox_folder)
                file_entries = files.entries
                expired_files = list(filter(lambda fl: (datetime.datetime.now() - fl.client_modified).days >= rec.days_to_remove, file_entries)) # noqa
                for file in expired_files:
                    dbx.files_delete_v2(file.path_display)
            if rec.notify_user:
                mail_template_success.send_mail(rec.id, force_send=True)
        except Exception as error:
            rec.generated_exception = error
            _logger.info('Dropbox Exception: %s', error)
            if rec.notify_user:
                mail_template_failed.send_mail(rec.id, force_send=True)
