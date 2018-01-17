# Part of Flectra. See LICENSE file for full copyright and licensing details.

from logging import info

from .test_scrum_common import TestScrumCommon


class TestScrumTask(TestScrumCommon):
    def setUp(self):
        super(TestScrumTask, self).setUp()

    def test_scrum_task(self):
        if not self.project_tasks:
            raise AssertionError('Error in data. Please Check Project Tasks.')
        info('Details of tasks:')
        for task in self.project_tasks:
            if not task.name:
                raise AssertionError(
                    'Error in data. Please Check Project Tasks Name.')
            info('Details of : %s' % task.name)
            if not task.project_id:
                raise AssertionError(
                    'Error in data. Please Check Project Tasks Project.')
            info('  Project : %s' % task.project_id.name)
            if not task.sprint_id:
                raise AssertionError(
                    'Error in data. Please Check Project Tasks Sprint.')
            info('  Sprint : %s' % task.sprint_id.name)
            info('  Assigned to : %s' % task.user_id.name)
            info('  Company : %s' % task.company_id.name)
            if not task.start_date and task.end_date:
                raise AssertionError(
                    'Error in data. Please Check Project Tasks Date.')
            info('  Date : %s - %s' % (task.start_date, task.end_date))
            info('  Actual End Date : %s' % task.actual_end_date)
            info('  Deadline : %s' % task.date_deadline)
            info('  Reference : %s' % task.task_seq)
            info('  Branch : %s' % task.branch_id.name)
            info('  Story : %s' % task.story_id.name)
            info('  Velocity : %d' % task.velocity)
            info('  Release Planning : %s' % task.release_planning_id.name)
            info('  Priority : %s' % task.priority)
            info('  Description : %s' % task.description)
