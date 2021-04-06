# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra.tests import common


class TestScrumCommon(common.SavepointCase):
    def setUp(self):
        super(TestScrumCommon, self).setUp()

        self.teams = [
            self.env.ref('project_scrum.project_team_1'),
            self.env.ref('project_scrum.project_team_2'),
            self.env.ref('project_scrum.project_team_3')
        ]

        self.user_roles = [
            self.env.ref('project_scrum.user_role_1'),
            self.env.ref('project_scrum.user_role_2'),
            self.env.ref('project_scrum.user_role_3')
        ]

        self.sprints = [
            self.env.ref('project_scrum.project_sprint_1'),
            self.env.ref('project_scrum.project_sprint_2'),
            self.env.ref('project_scrum.project_sprint_3'),
            self.env.ref('project_scrum.project_sprint_4'),
            self.env.ref('project_scrum.project_sprint_5')
        ]

        self.project_tasks = [
            self.env.ref('project_scrum.project_task_1'),
            self.env.ref('project_scrum.project_task_2'),
            self.env.ref('project_scrum.project_task_3'),
            self.env.ref('project_scrum.project_task_4'),
            self.env.ref('project_scrum.project_task_6'),
            self.env.ref('project_scrum.project_task_7'),
            self.env.ref('project_scrum.project_task_8'),
            self.env.ref('project_scrum.project_task_9'),
            self.env.ref('project_scrum.project_task_10'),
            self.env.ref('project_scrum.project_task_11'),
            self.env.ref('project_scrum.project_task_12'),
            self.env.ref('project_scrum.project_task_13'),
            self.env.ref('project_scrum.project_task_14')
        ]

        self.users = [
            self.env.ref('project_scrum.user_1'),
            self.env.ref('project_scrum.user_2'),
            self.env.ref('project_scrum.user_3')
        ]

        self.release_plans = [
            self.env.ref('project_scrum.release_planning_1'),
            self.env.ref('project_scrum.release_planning_2'),
            self.env.ref('project_scrum.release_planning_3'),
            self.env.ref('project_scrum.release_planning_4'),
            self.env.ref('project_scrum.release_planning_5')
        ]

        self.story_priorities = [
            self.env.ref('project_scrum.story_priority_1'),
            self.env.ref('project_scrum.story_priority_2'),
            self.env.ref('project_scrum.story_priority_3')
        ]

        self.story_types = [
            self.env.ref('project_scrum.story_type_1'),
            self.env.ref('project_scrum.story_type_2')
        ]

        self.stories = [
            self.env.ref('project_scrum.project_story_1'),
            self.env.ref('project_scrum.project_story_2'),
            self.env.ref('project_scrum.project_story_3')
        ]

        self.project = self.env.ref('project_scrum.demo_project_1')

        self.sprint_planning_line = self.env['sprint.planning.line']
