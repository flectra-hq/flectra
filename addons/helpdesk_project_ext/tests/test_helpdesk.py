# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase


class TestHelpdesk(TransactionCase):

    def setUp(self):
        """ setUp ***"""
        super(TestHelpdesk, self).setUp()
        self.helpdesk_id = self.env.ref('helpdesk_basic.helpdesk_ticket')

    def test_00_helpdesk_project_workflow(self):
        self.assertFalse(self.helpdesk_id._compute_task_count(),
                         'Helpdesk task should not be created.')
        self.helpdesk_id.action_create_task()
        self.helpdesk_id._compute_task_count()
        self.assertEqual(self.helpdesk_id.task_count, 1,
                         'Helpdesk task creation process fails')
