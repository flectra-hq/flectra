# Part of Flectra. See LICENSE file for full copyright and licensing details.

from logging import info

from .test_scrum_common import TestScrumCommon


class TestScrumStory(TestScrumCommon):
    def setUp(self):
        super(TestScrumStory, self).setUp()

    def test_scrum_story(self):
        if not self.story_priorities:
            raise AssertionError(
                'Error in data. Please check for story priorities.')
        self.check_priority(self.story_priorities)

        if not self.story_types:
            raise AssertionError(
                'Error in data. Please check for story types.')
        self.check_type(self.story_types)

        if not self.stories:
            raise AssertionError(
                'Error in data. Please check for story data.')
        self.check_story(self.stories)

    def check_priority(self, priorities):
        info('Details of Priorities :')
        info('  Code : Name')
        for priority in priorities:
            info('  %s : %s' % (priority.code, priority.name))

    def check_type(self, types):
        info('Details of Story Types :')
        info('  Code : Name')
        for type in types:
            info('  %s : %s' % (type.code, type.name))

    def check_story(self, stories):
        info('Details of Stories:')
        for story in stories:
            if not story.name:
                raise AssertionError(
                    'Error in data. Please check for story name.')
            info('Story : %s' % story.name)
            if not story.sprint_id:
                raise AssertionError(
                    'Error in data. Please check for story sprint value.')
            info('  Sprint : %s' % story.sprint_id.name)
            info('  Priority : %s' % story.priority_id.name)
            info('  Owner : %s' % story.owner_id.name)
            info('  Branch : %s' % story.branch_id.name)
            info('  Type : %s' % story.story_type_id.name)
            info('  Actual Velocity : %d' % story.actual_velocity)
            info('  Estimated Velocity : %s' % story.estimated_velocity	)
            info('  Description : %s' % story.description)
