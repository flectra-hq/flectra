# Part of Flectra See LICENSE file for full copyright and licensing details.

import json
from datetime import datetime, timedelta

from babel.dates import format_datetime, format_date
from flectra import api, fields, models, _
from flectra.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class IssueType(models.Model):
    _name = 'issue.type'
    _description = 'Issue Type'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    reporting_template = fields.Text(string='Reporting Template')
    color = fields.Integer(string='Color Index')
    stages = fields.Char(compute='_compute_stages')
    kanban_dashboard_graph = fields.Text(
        compute='_compute_kanban_dashboard_graph')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '%s-%s' % (record.code, record.name)))
        return result

    @api.multi
    def _compute_stages(self):
        ticket = self.env['helpdesk.ticket']
        stage_ids = self.env['helpdesk.stage'].search([])
        for type in self:
            stages = []
            for stage in stage_ids:
                context = \
                    "{'search_default_stage_id': %d, " \
                    "'search_default_issue_type_id': %d}" % (stage.id, type.id)
                tickets = ticket.search(
                    [('issue_type_id', '=', type.id),
                     ('stage_id', '=', stage.id)])
                stages.append({'key': stage.name, 'value': len(tickets.ids),
                               'context': context,
                               'ticket_ids': tickets.ids})
            type.stages = json.dumps(stages)

    @api.multi
    def action_create_new(self):
        ctx = self._context.copy()
        model = 'helpdesk.ticket'
        view_id = self.env.ref('helpdesk_basic.view_helpdesk_form').id
        return {
            'name': _('Create Ticket'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': model,
            'view_id': view_id,
            'context': ctx,
        }

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
                        format_date(end_week, 'MMM',
                                    locale=self._context.get(
                                        'lang') or 'en_US')
                else:
                    label = \
                        format_date(start_week, 'd MMM',
                                    locale=self._context.get('lang') or 'en_US'
                                    ) + '-' + format_date(
                            end_week, 'd MMM',
                            locale=self._context.get('lang') or 'en_US')
            data.append({
                'label': label,
                'value': 0.0,
                'type': 'past' if i < 0 else 'future'})

        select_sql_clause = 'SELECT count(*) FROM helpdesk_ticket AS h ' \
                            'WHERE issue_type_id = %(issue_type_id)s'
        query_args = {'issue_type_id': self.id}
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
                         "' and end_date < '" + next_date.strftime(DF) + \
                         "')"
                start_date = next_date

        self.env.cr.execute(query, query_args)
        query_results = self.env.cr.dictfetchall()
        for index in range(0, len(query_results)):
            if query_results[index]:
                data[index]['value'] = query_results[index].get('count')
        return [{'values': data}]
