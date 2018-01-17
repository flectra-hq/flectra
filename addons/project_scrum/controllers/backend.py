# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import http
from flectra.http import request
from datetime import datetime


class Sprint(http.Controller):

    @http.route('/project_scrum/get_sprints_data', type='json', auth='user')
    def fetch_sprints_data(self):
        res = {}

        total_sprints = request.env['project.sprint'].search_count([])
        total_tasks = request.env['project.task'].search_count([])
        total_stories = request.env['project.story'].search_count([])
        total_projects = request.env['project.project'].search_count([])
        sprint_ids = request.env['project.sprint'].search_read(
            [], ['id', 'name'])

        res.update({
            'total_sprints': total_sprints,
            'total_tasks': total_tasks,
            'total_stories': total_stories,
            'total_projects': total_projects,
            'sprint_ids': sprint_ids,
        })

        return res

    @http.route('/project_scrum/get_sprint_data_for_chart', type='json',
                auth='user')
    def fetch_data_for_chart(self):
        data = []
        sprint_ids = request.env['project.sprint'].search([])

        for sprint in sprint_ids:
            start = datetime.strptime(sprint.start_date, '%Y-%m-%d').date()
            end = datetime.strptime(sprint.end_date, '%Y-%m-%d').date()
            diff = (end - start).days

            data.append({
                'sprint_seq': sprint.sprint_seq or '/',
                'velocity': sprint.estimated_velocity or 0,
                'no_of_days': diff,
            })

        return data

    @http.route('/project_scrum/get_sprint_data', type='json', auth='user')
    def fetch_sprint_data(self, sprint_id):
        data = []

        if sprint_id:
            sprint_obj = request.env['project.sprint'].browse(
                int(sprint_id))
            sprint_velocity = sprint_obj.estimated_velocity
            task_ids = request.env['project.task'].search([
                ('sprint_id', '=', int(sprint_id))
            ])

            for task in task_ids:
                per = (float(task.velocity) * 100) / float(sprint_velocity)
                data.append({
                    'velocity': task.velocity,
                    'task_seq': task.task_seq or '/',
                    'per': round(per, 2),
                    'user': task.user_id.name or '',
                    'id': task.id,
                })
            return data

    @http.route('/project_scrum/get_sprints_task_data', type='json',
                auth='user')
    def fetch_sprints_task_data(self, sprint_id):
        res = {}

        if sprint_id:
            domain = [('sprint_id', '=', int(sprint_id))]

            total_tasks = request.env['project.task'].search_count(domain)
            total_stories = request.env['project.story'].search_count(domain)

            res.update({
                'total_tasks': total_tasks,
                'total_stories': total_stories,
            })

            return res

    @http.route('/project_scrum/get_line_chart_data', type='json',
                auth='user')
    def fetch_line_chart_data(self):
        data = []
        sprint_ids = request.env['project.sprint'].search([])
        for sprint in sprint_ids:
            per = float(
                (sprint.actual_velocity * 100) / sprint.estimated_velocity
                if sprint.estimated_velocity > 0.0 else 0.0)
            data.append({
                'sprint_seq': sprint.sprint_seq or '/',
                'per': per,
                'velocity': sprint.estimated_velocity or 0.0,
            })
        return data
