# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra.tests.common import TransactionCase


class TestHelpdesk(TransactionCase):

    def setUp(self):
        """ setUp ***"""
        super(TestHelpdesk, self).setUp()
        self.helpdesk_id = self.env.ref('helpdesk_basic.helpdesk_ticket')

    def test_00_helpdesk_workflow(self):
        team = self.env.ref('helpdesk_basic.helpdesk_software')
        issue_type = self.env.ref('helpdesk_basic.issue_type_software')
        tag = self.env.ref('helpdesk_basic.helpdesk_tag_new')
        stage = self.env.ref('helpdesk_basic.helpdesk_stage_draft')

        new_helpdesk = self.env['helpdesk.ticket'].create({
            'name': 'Testing helpdesk ticket',
            'issue_type_id': issue_type.id,
            'priority': '2',
            'tag_ids': [(6, 0, [tag.id])],
            'team_id': team.id,
            'stage_id': stage.id,
            'assigned_to_id': self.env.ref('base.user_demo').id
        })

        self.assertTrue(new_helpdesk,
                        'Helpdesk Issue ticket creation failed')
        new_helpdesk.assigned_to_id = self.env.ref('base.user_root').id

        team._compute_helpdesk_count()
        count_before = team.helpdesk_count
        new_helpdesk.onchange_team_id()
        new_helpdesk.team_id = self.env.ref(
            'helpdesk_basic.helpdesk_hardware').id
        self.assertFalse(
            new_helpdesk.assigned_to_id.id,
            'Assigned to must be reset on change of helpdesk team')
        team._compute_helpdesk_count()
        count_after = team.helpdesk_count
        self.assertEqual(count_before, count_after + 1,
                         'Helpdesk count is not working properly')

        new_helpdesk.issue_type_id = self.env.ref(
            'helpdesk_basic.issue_type_hardware').id
        new_helpdesk.onchange_issue_type_id()
        # self.assertFalse(
        #     new_helpdesk.team_id.id,
        #     'Team must be reset on change of helpdesk issue type')

        action = new_helpdesk.issue_type_id.action_create_new()
        self.assertTrue(action,
                        'Helpdesk Issue ticket creation form from '
                        'kanban view not working correctly')

        action = new_helpdesk.action_get_team()
        self.assertTrue(action, 'Helpdesk team redirectiom form from '
                                'dashboard view not working correctly')

        action = new_helpdesk.action_get_issue_type()
        self.assertTrue(action, 'Helpdesk team redirectiom form from '
                                'dashboard view not working correctly')

        new_helpdesk.team_id = team.id
        member_before = len(new_helpdesk.team_id.member_ids.ids)
        new_helpdesk.team_id.member_ids = \
            [(4, self.env.ref('base.demo_user0').id)]
        member_after = len(new_helpdesk.team_id.member_ids.ids)
        self.assertEqual(member_after, member_before + 1,
                         'Helpdesk Team members not updated properly')

        self.helpdesk_id.issue_type_id._compute_stages()
        self.assertTrue(
            self.helpdesk_id.issue_type_id.stages,
            'Helpdesk Issue stages details in kanban view working correctly')

        action = self.helpdesk_id.issue_type_id.action_create_new()
        self.assertTrue(
            action,
            'Helpdesk Issue create button in kanban view working correctly')
