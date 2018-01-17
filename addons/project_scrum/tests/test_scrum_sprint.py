# Part of Flectra. See LICENSE file for full copyright and licensing details.

from logging import info

from .test_scrum_common import TestScrumCommon


class TestScrumSprint(TestScrumCommon):
    def setUp(self):
        super(TestScrumSprint, self).setUp()

    def test_scrum_sprint(self):
        # self.check_user_roles(self.user_roles)
        self.check_sprint(self.sprints)

    def check_user_roles(self, roles):
        if not roles:
            raise AssertionError('Error in data. Please check user role data.')
        info('Details of Roles :')
        info('Code : name')
        for role in roles:
            info('  %s : %s' % (role.code, role.name))

    def check_sprint(self, sprints):
        if not sprints:
            raise AssertionError('Error in data. Please check sprint data.')
        info('Details of Sprints :')
        for sprint in sprints:
            info('Sprint : %s' % sprint.name)
            info('  Sequence : %s' % sprint.sprint_seq)
            info('  Project : %s' % sprint.project_id.name)
            info('  Team : %s' % sprint.team_id.name)
            info('  Date : %s - %s' % (sprint.start_date, sprint.end_date))
            info('  Planning Meeting Date : %s' % sprint.meeting_date)
            info('  Goal of Sprint : %s' % sprint.goal_of_sprint)
            info('  Branch : %s' % sprint.branch_id.name)
            info('  Daily Scrum Time : %f' % sprint.hour)
            info('  Duration (In Days): %d' % sprint.duration)
            info('  Estimated Velocity : %d' % sprint.estimated_velocity)
            info('  Actual Velocity	: %d' % sprint.actual_velocity)
            info('  Business Days : %d' % sprint.working_days)
            info('  Holiday (Hours / Days) : %s' % sprint.holiday_type)
            info('  Holiday Count : %f' % sprint.holiday_count)
            info('  Productivity Hours : %s' % sprint.productivity_hours)
            info('  Productivity  : %f' % sprint.productivity_per)

            lines = self.sprint_planning_line.search(
                [('sprint_id', '=', sprint.id)])
            if not lines:
                raise AssertionError(
                    'Error in data. Please check spring planning lines '
                    'for sprint %s' % sprint.name)

            info('  Spring Planning :')
            for line in lines:
                info('      User : %s' % line.user_id.name)
                info('          Role : %s' % line.role_id.name)
                info('          Available : %s' % line.available_per)
                info('          Productivity Hour : '
                     '%s' % line.productivity_hours)
                info('          Sprint hour : %s' % line.sprint_hours)
                info('          Off Hour : %s' % line.off_hours)
                info('          Total Hour: %s' % line.total_hours)
