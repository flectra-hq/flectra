# Part of Flectra. See LICENSE file for full copyright and licensing details.

from logging import info

from .test_scrum_common import TestScrumCommon


class TestScrumReleasePlanning(TestScrumCommon):
    def setUp(self):
        super(TestScrumReleasePlanning, self).setUp()

    def test_scrum_release_planning(self):
        if not self.release_plans:
            raise AssertionError(
                'Error in data. Please check for release planning.')
        info('Details of release planning:')
        for plan in self.release_plans:
            info('Release Plan : %s' % plan.name)
            info('  Release Date : %s' % plan.release_date)
            info('  Sprint : %s' % plan.sprint_id.name)
            info('  Branch : %s' % plan.branch_id.name)
            info('  Priority : %s' % plan.priority)
            info('  Sprint Velocity : %s' % plan.velocity)
