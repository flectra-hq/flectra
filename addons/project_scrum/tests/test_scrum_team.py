# Part of Flectra. See LICENSE file for full copyright and licensing details.

from logging import info

from .test_scrum_common import TestScrumCommon


class TestScrumTeam(TestScrumCommon):
    def setUp(self):
        super(TestScrumTeam, self).setUp()

    def test_scrum_team(self):
        if not self.teams:
            raise AssertionError(
                'Error in data. Please check for Team in Scrum.')
        info('Details of Teams of Scrum.....')
        for team in self.teams:
            if not (team.name and team.project_id):
                raise AssertionError(
                    'Error in data. Please check for Team in Scrum.')

            info('Team Name : %s' % team.name)
            info('  Description : %s' % team.description)
            info('  Strength : %s' % team.strength)
            info('  Project : %s' % team.project_id.name)
            info('  Scrum Master : %s' % team.master_id.name)
            if team.member_ids:
                info('  Members : %d' % len(team.member_ids))
                for member in team.member_ids:
                    info('      %s' % member.name)
            info('  Branch : %s' % team.branch_id.name)
