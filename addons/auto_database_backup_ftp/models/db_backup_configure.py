# Part of Flectra. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################

import datetime
import ftplib
import logging
import tempfile

import flectra
from flectra import _, fields, models
from flectra.exceptions import UserError

_logger = logging.getLogger(__name__)


class AutoDatabaseBackup(models.Model):
    _inherit = 'db.backup.configure'
    _description = 'Automatic Database Backup'

    backup_destination = fields.Selection(selection_add=[('ftp', 'FTP')],
                                          ondelete={'ftp': 'set default'})

    ftp_host = fields.Char(string='FTP Host')
    ftp_port = fields.Char(string='FTP Port', default=21)
    ftp_user = fields.Char(string='FTP User', copy=False)
    ftp_password = fields.Char(string='FTP Password', copy=False)
    ftp_path = fields.Char(string='FTP Path')

    def test_ftp_connection(self):
        """
        Test the ftp connection using entered credentials
        """
        try:
            ftp_server = ftplib.FTP()
            ftp_server.connect(self.ftp_host, int(self.ftp_port))
            ftp_server.login(self.ftp_user, self.ftp_password)
            ftp_server.quit()
        except Exception as e:
            raise UserError(_("FTP Exception: %s", e))
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

    def backup_to_ftp(self, rec):
        mail_template_success = self.env.ref('auto_database_backup.'
                                             'mail_template_data_db_backup_successful')
        mail_template_failed = self.env.ref('auto_database_backup.'
                                            'mail_template_data_db_backup_failed')
        backup_time = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = "%s_%s.%s" % (rec.db_name, backup_time, rec.backup_format)
        try:
            ftp_server = ftplib.FTP()
            ftp_server.connect(rec.ftp_host, int(rec.ftp_port))
            ftp_server.login(rec.ftp_user, rec.ftp_password)
            ftp_server.encoding = "utf-8"
            temp = tempfile.NamedTemporaryFile(suffix='.%s' % rec.backup_format)
            try:
                ftp_server.cwd(rec.ftp_path)
            except ftplib.error_perm:
                ftp_server.mkd(rec.ftp_path)
                ftp_server.cwd(rec.ftp_path)
            with open(temp.name, "wb+") as tmp:
                flectra.service.db.dump_db(rec.db_name, tmp, rec.backup_format)
            ftp_server.storbinary('STOR %s' % backup_filename, open(temp.name, "rb"))
            if rec.auto_remove:
                files = ftp_server.nlst()
                for f in files:
                    create_time = \
                        datetime.datetime.strptime(ftp_server.sendcmd('MDTM ' + f)[4:],
                                                   "%Y%m%d%H%M%S")
                    diff_days = (datetime.datetime.now() - create_time).days
                    if diff_days >= rec.days_to_remove:
                        ftp_server.delete(f)
            ftp_server.quit()
            if rec.notify_user:
                mail_template_success.send_mail(rec.id, force_send=True)
        except Exception as e:
            rec.generated_exception = e
            _logger.info('FTP Exception: %s', e)
            if rec.notify_user:
                mail_template_failed.send_mail(rec.id, force_send=True)
