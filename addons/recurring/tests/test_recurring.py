# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import _
from flectra.exceptions import UserError

from flectra.tests.common import TransactionCase
import logging
_logger = logging.getLogger(__name__)


class RecurringTransactionCase(TransactionCase):

    def setUp(self):
        super(RecurringTransactionCase, self).setUp()
        self.recurring_id = self.env.ref("recurring.recurring_partner0")

    def check_recurring(self):
        self.recurring_id.set_process()
        if not self.recurring_id.cron_id:
            raise UserError(_("Cron is not created"))
        else:
            self.recurring_id.cron_id.method_direct_trigger()
            try:
                self.recurring_id.unlink()
            except Exception as e:
                _logger.info(
                    "You cannot delete an active recurring!")
            self.recurring_id.set_done()
            if not self.recurring_id.state == 'done':
                raise UserError(_("Recurring is in running state"))
            self.recurring_id.set_draft()
            if not self.recurring_id.state == 'draft':
                raise UserError(_("Recurring is not in draft state"))

    def test_01_recurring(self):
        self.check_recurring()
