# Part of Flectra. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################

import datetime
import errno
import logging
import tempfile

import paramiko

import flectra
from flectra import _, fields, models
from flectra.exceptions import UserError

_logger = logging.getLogger(__name__)


class AutoDatabaseBackup(models.Model):
    _inherit = 'db.backup.configure'
    _description = 'Automatic Database Backup'

    backup_destination = fields.Selection(selection_add=[('sftp', 'SFTP')],
                                          ondelete={'sftp': 'set default'})

    sftp_host = fields.Char(string='SFTP Host')
    sftp_port = fields.Char(string='SFTP Port', default=22)
    sftp_user = fields.Char(string='SFTP User', copy=False)
    sftp_password = fields.Char(string='SFTP Password', copy=False)
    sftp_path = fields.Char(string='SFTP Path')

    def test_sftp_connection(self):
        """
        Test the sftp connection using entered credentials
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(hostname=self.sftp_host,
                           username=self.sftp_user,
                           password=self.sftp_password,
                           port=self.sftp_port)
            sftp = client.open_sftp()
            sftp.close()
        except Exception as e:
            raise UserError(_("SFTP Exception: %s", e))
        finally:
            client.close()
        title = _("Connection Test Succeeded!")
        message = _("Everything seems properly set up!")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'sticky': False,
            }
        }

    def backup_to_sftp(self, rec):
        mail_template_success = self.env.ref('auto_database_backup.'
                                             'mail_template_data_db_backup_successful')
        mail_template_failed = self.env.ref('auto_database_backup.'
                                            'mail_template_data_db_backup_failed')
        backup_time = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = "%s_%s.%s" % (rec.db_name, backup_time, rec.backup_format)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(hostname=rec.sftp_host,
                           username=rec.sftp_user,
                           password=rec.sftp_password,
                           port=rec.sftp_port)
            sftp = client.open_sftp()
            temp = tempfile.NamedTemporaryFile(suffix='.%s' % rec.backup_format)
            with open(temp.name, "wb+") as tmp:
                flectra.service.db.dump_db(rec.db_name, tmp, rec.backup_format)
            try:
                sftp.chdir(rec.sftp_path)
            except IOError as e:
                if e.errno == errno.ENOENT:
                    sftp.mkdir(rec.sftp_path)
                    sftp.chdir(rec.sftp_path)
            sftp.put(temp.name, backup_filename)
            if rec.auto_remove:
                files = sftp.listdir()
                expired = list(filter(lambda fl: (datetime.datetime.now() - datetime.datetime.fromtimestamp(sftp.stat(fl).st_mtime)).days >= rec.days_to_remove, files)) # noqa
                for file in expired:
                    sftp.unlink(file)
            sftp.close()
            if rec.notify_user:
                mail_template_success.send_mail(rec.id, force_send=True)
        except Exception as e:
            rec.generated_exception = e
            _logger.info('SFTP Exception: %s', e)
            if rec.notify_user:
                mail_template_failed.send_mail(rec.id, force_send=True)
        finally:
            client.close()
