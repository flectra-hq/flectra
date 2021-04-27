# Part of flectra See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase


class TestHelpdeskForum(TransactionCase):

    def setUp(self):
        """ setUp ***"""
        super(TestHelpdeskForum, self).setUp()

    def test_00_helpdesk_forum_workflow(self):
        forum1 = self.env['forum.forum'].create({
            'name': 'Help',
            'description': 'This community is for professionals and enthusiasts of our products and services. Share and discuss the best content and new marketing ideas, build your professional profile and become a better marketer together.'
        })
        team = self.env['helpdesk.team'].create({
            'name': 'Test team software',
            'alias_name': 'test_team_software',
            'issue_type_ids':
                [(4, self.env.ref('helpdesk_basic.issue_type_software').id)],
            'stage_ids':
                [(6, 0, [self.env.ref('helpdesk_basic.helpdesk_stage_new').id,
                         self.env.ref(
                             'helpdesk_basic.helpdesk_stage_in_progress').id,
                         self.env.ref(
                             'helpdesk_basic.helpdesk_stage_done').id])],
            'member_ids': [(6, 0, [self.env.ref('base.user_demo').id])],
            'forum_id': forum1.id
        })
        self.assertTrue(team.forum_id, 'Helpdesk Team forum creation fails')
