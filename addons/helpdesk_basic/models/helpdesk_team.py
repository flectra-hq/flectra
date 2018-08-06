# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.tools.safe_eval import safe_eval
from flectra.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime, timedelta
from babel.dates import format_datetime, format_date
import json


class HelpdeskTeam(models.Model):
    _name = 'helpdesk.team'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.alias.mixin']
    _description = 'Helpdesk Team'

    name = fields.Char(string='Helpdesk Team', translate=True,
                       track_visibility='always', required=True)
    active = fields.Boolean(string='Active', default=True)
    color = fields.Integer(string='Color Index')
    member_ids = fields.Many2many('res.users', string='Members')
    alias_id = fields.Many2one('mail.alias', 'Alias', ondelete='restrict')
    issue_type_ids = fields.Many2many('issue.type', string='Issue Type')
    helpdesk_count = fields.Integer(compute='_compute_helpdesk_count',
                                    string='Total Helpdesk')
    stage_ids = fields.Many2many('helpdesk.stage', string='Stages')
    kanban_dashboard_graph = fields.Text(
        compute='_compute_kanban_dashboard_graph')

    @api.multi
    def _compute_helpdesk_count(self):
        for team in self:
            team.helpdesk_count = self.env['helpdesk.ticket'].search_count([
                ('team_id', '=', team.id)])

    @api.multi
    def get_alias_model_name(self, vals):
        return vals.get('alias_model', 'helpdesk.ticket')

    @api.multi
    def get_alias_values(self):
        self.ensure_one()
        values = super(HelpdeskTeam, self).get_alias_values()
        values['alias_defaults'] = defaults = safe_eval(
            self.alias_defaults or "{}")
        defaults['team_id'] = self.id
        return values

    @api.model
    def create(self, values):
        res = super(HelpdeskTeam, self).create(values)
        res.message_subscribe_users(user_ids=res.member_ids.ids)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('member_ids', False):
            self.message_subscribe_users(user_ids=self.member_ids.ids)
        result = super(HelpdeskTeam, self).write(vals)
        if 'alias_defaults' in vals:
            for team in self:
                team.alias_id.write(team.get_alias_values())
        return result

    @api.multi
    def _compute_kanban_dashboard_graph(self):
        for record in self:
            record.kanban_dashboard_graph = json.dumps(
                record.get_bar_graph_datas())

    @api.multi
    def get_bar_graph_datas(self):
        data = []
        today = datetime.strptime(fields.Date.context_today(self), DF)
        data.append({'label': _('Past'), 'value': 0.0, 'type': 'past'})
        day_of_week = int(format_datetime(today, 'e', locale=self._context.get(
            'lang') or 'en_US'))
        first_day_of_week = today + timedelta(days=-day_of_week + 1)
        for i in range(-1, 4):
            if i == 0:
                label = _('This Week')
            elif i == 3:
                label = _('Future')
            else:
                start_week = first_day_of_week + timedelta(days=i * 7)
                end_week = start_week + timedelta(days=6)
                if start_week.month == end_week.month:
                    label = \
                        str(start_week.day) + '-' + str(end_week.day) + ' ' + \
                        format_date(end_week, 'MMM', locale=self._context.get(
                            'lang') or 'en_US')
                else:
                    label = \
                        format_date(start_week, 'd MMM',
                                    locale=self._context.get('lang') or 'en_US'
                                    ) + '-' + format_date(
                            end_week, 'd MMM',
                            locale=self._context.get('lang') or'en_US')
            data.append(
                {'label': label,
                 'value': 0.0,
                 'type': 'past' if i < 0 else 'future'})

        select_sql_clause = 'SELECT count(*) FROM helpdesk_ticket AS h ' \
                            'WHERE team_id = %(team_id)s'
        query_args = {'team_id': self.id}
        query = ''
        start_date = (first_day_of_week + timedelta(days=-7))
        for i in range(0, 6):
            if i == 0:
                query += "(" + select_sql_clause + " and start_date < '" + \
                         start_date.strftime(DF) + "')"
            elif i == 5:
                query += " UNION ALL (" + select_sql_clause + \
                         " and start_date >= '" + \
                         start_date.strftime(DF) + "')"
            else:
                next_date = start_date + timedelta(days=7)
                query += " UNION ALL (" + select_sql_clause + \
                         " and start_date >= '" + start_date.strftime(DF) + \
                         "' and start_date < '" + next_date.strftime(DF) + \
                         "')"
                start_date = next_date
        self.env.cr.execute(query, query_args)
        query_results = self.env.cr.dictfetchall()
        for index in range(0, len(query_results)):
            if query_results[index]:
                data[index]['value'] = query_results[index].get('count')
        return [{'values': data}]
