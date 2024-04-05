# Part of Flectra. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################

import datetime
import logging
import os

import flectra
from flectra import _, api, fields, models
from flectra.exceptions import ValidationError
from flectra.service import db

_logger = logging.getLogger(__name__)


class AutoDatabaseBackup(models.Model):
    _name = 'db.backup.configure'
    _description = 'Automatic Database Backup'

    name = fields.Char(string='Name', required=True)
    db_name = fields.Char(string='Database Name', required=True)
    backup_format = fields.Selection([
        ('zip', 'Zip'),
        ('dump', 'Dump')
    ], string='Backup Format', default='zip', required=True)
    backup_destination = fields.Selection([
        ('local', 'Local Storage')
    ], string='Backup Destination', default='local')
    backup_path = fields.Char(string='Backup Path',
                              help='Local storage directory path')
    active = fields.Boolean(default=True)
    auto_remove = fields.Boolean(string='Remove Old Backups')
    days_to_remove =\
        fields.Integer(string='Remove After',
                       help='Automatically delete stored backups'
                            ' after this specified number of days')
    notify_user =\
        fields.Boolean(string='Notify User',
                       help='Send an email notification to user '
                            'when the backup operation is successful or failed')
    user_id = fields.Many2one('res.users', string='User')
    backup_filename = fields.Char(string='Backup Filename',
                                  help='For Storing generated backup filename')
    generated_exception =\
        fields.Char(string='Exception',
                    help='Exception Encountered while Backup generation')

    @api.constrains('db_name')
    def _check_db_credentials(self):
        """
        Validate entered database name and master password
        """
        database_list = db.list_dbs()
        if self.db_name not in database_list:
            raise ValidationError(_("Invalid Database Name!"))

    def create_database_backup(self):
        mail_template_success = self.env.ref('auto_database_backup.'
                                             'mail_template_data_db_backup_successful')
        mail_template_failed = self.env.ref('auto_database_backup.'
                                            'mail_template_data_db_backup_failed')
        backup_time = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = "%s_%s.%s" % (self.db_name, backup_time, self.backup_format)
        self.backup_filename = backup_filename
        # Local backup
        if self.backup_destination == 'local':
            try:
                if not os.path.isdir(self.backup_path):
                    os.makedirs(self.backup_path)
                backup_file = os.path.join(self.backup_path, backup_filename)
                f = open(backup_file, "wb")
                flectra.service.db.dump_db(self.db_name, f, self.backup_format)
                f.close()
                # remove older backups
                if self.auto_remove:
                    for filename in os.listdir(self.backup_path):
                        file = os.path.join(self.backup_path, filename)
                        create_time = \
                            datetime.datetime.fromtimestamp(os.path.getctime(file))
                        backup_duration = datetime.datetime.utcnow() - create_time
                        if backup_duration.days >= self.days_to_remove:
                            os.remove(file)
                if self.notify_user:
                    mail_template_success.send_mail(self.id, force_send=True)
            except Exception as e:
                self.generated_exception = e
                _logger.info('FTP Exception: %s', e)
                if self.notify_user:
                    mail_template_failed.send_mail(self.id, force_send=True)
        else:
            method_name = 'backup_to_' + self.backup_destination
            getattr(self, method_name)(self)

    def _schedule_auto_backup(self):
        """
        Function for generating and storing backup
        Database backup for all the active records in
         backup configuration model will be created
        """
        records = self.search([])
        for rec in records:
            rec.create_database_backup()


class Module(models.Model):
    _inherit = "ir.module.module"

    def button_immediate_upgrade(self):
        """
        Upgrade the selected module(s) immediately and fully,
        return the next res.config action to execute
        """
        auto_backup = self.env['ir.config_parameter'].sudo().get_param('auto_backup')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Upgrade Confirmation',
            'res_model': 'module.upgrade.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'auto_backup': auto_backup}
        }
