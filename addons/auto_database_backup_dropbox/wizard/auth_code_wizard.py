# Part of Flectra. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################

from flectra import api, fields, models


class AuthenticationWizard(models.TransientModel):
    _name = 'authentication.wizard'
    _description = 'Authentication Code Wizard'

    dropbox_authorization_code = fields.Char(string='Dropbox Authorization Code')
    dropbox_auth_url = fields.Char(string='Dropbox Authentication URL',
                                   compute='_compute_dropbox_auth_url')

    @api.depends('dropbox_authorization_code')
    def _compute_dropbox_auth_url(self):
        backup_config =\
            self.env['db.backup.configure'].browse(self.env.context.get('active_id'))
        dropbox_auth_url = backup_config.get_dropbox_auth_url()
        for rec in self:
            rec.dropbox_auth_url = dropbox_auth_url

    def action_setup_dropbox_token(self):
        backup_config =\
            self.env['db.backup.configure'].browse(self.env.context.get('active_id'))
        backup_config.set_dropbox_refresh_token(self.dropbox_authorization_code)
