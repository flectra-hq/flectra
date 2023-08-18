# coding: utf-8
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
from flectra import models, fields, api
from flectra.tools import float_round
from dateutil.relativedelta import relativedelta

DEFAULT_MONTH_RANGE = 3


class HrTimesheetInvoiceFactor(models.Model):
    _name = "hr_timesheet_invoice.factor"
    _description = "Invoice Rate"

    name = fields.Char('Name', translate=True)
    factor = fields.Float(string='Invoiceable Factor',
                          required=True, help="Invoiceable in percentage")
    not_invoiceable = fields.Boolean(string='Not Invoiceable')


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _description = "Account Analytic Line"

    invoicable_id = fields.Many2one('hr_timesheet_invoice.factor',
                                    string="Invoiceable(%)")
    calculated_hours_invoice = fields.Float(string="Calculated Hours",
                                            compute_sudo=True, store=True,
                                            compute="_compute_calculated_hours")

    @api.depends('unit_amount', 'invoicable_id')
    def _compute_calculated_hours(self):
        for rec in self:
            if rec.invoicable_id.not_invoiceable:
                rec.update({
                    'calculated_hours_invoice': 0.0,
                })
            elif rec.invoicable_id.factor != 0.0:
                calculated_hours = (rec.unit_amount * rec.invoicable_id.factor / 100)
                rec.update({
                    'calculated_hours_invoice': calculated_hours,
                })
            else:
                for a in rec:
                    a.calculated_hours_invoice = a.unit_amount


class Project(models.Model):
    _inherit = 'project.project'
    _description = "Project Project"

    def _plan_prepare_values(self):
        res = super(Project, self)._plan_prepare_values()
        uom_hour = self.env.ref('uom.product_uom_hour')
        hour_rounding = uom_hour.rounding
        company_uom = self.env.company.timesheet_encode_uom_id
        is_uom_day = company_uom == self.env.ref('uom.product_uom_day')
        billable_types = ['non_billable', 'non_billable_project',
                          'billable_time', 'non_billable_timesheet',
                          'billable_fixed']
        canceled_hours_domain = [('project_id', 'in', self.ids),
                                 ('timesheet_invoice_type', '!=', False),
                                 ('so_line.state', '=', 'cancel')]

        dashboard_values = {
            'time': dict.fromkeys(billable_types + ['total'], 0.0),
            'rates': dict.fromkeys(billable_types + ['total'], 0.0),
            'profit': {
                'invoiced': 0.0,
                'to_invoice': 0.0,
                'cost': 0.0,
                'total': 0.0,
            }
        }

        total_canceled_hours = sum(
            self.env['account.analytic.line'].search(
                canceled_hours_domain).mapped('calculated_hours_invoice'))
        canceled_hours = float_round(total_canceled_hours,
                                     precision_rounding=hour_rounding)
        dashboard_values['time']['total'] += canceled_hours
        dashboard_values_total_time = dashboard_values['time']['total']
        res['dashboard']['time'].update({
            'canceled': canceled_hours,
            'total': dashboard_values_total_time
        })

        dashboard_domain = [('project_id', 'in', self.ids),
                            ('timesheet_invoice_type', '!=', False),
                            ('calculated_hours_invoice', '!=', False), '|',
                            ('so_line', '=', False), ('so_line.state', '!=', 'cancel')]
        dashboard_data = self.env['account.analytic.line'].read_group(
            dashboard_domain, ['calculated_hours_invoice',
                               'timesheet_invoice_type'],
            ['timesheet_invoice_type'])

        dashboard_total_hours = sum(
            [data['calculated_hours_invoice'] for
             data in dashboard_data]) + total_canceled_hours

        for data in dashboard_data:
            billable_type = data['timesheet_invoice_type']
            amount = float_round(data.get('calculated_hours_invoice'),
                                 precision_rounding=hour_rounding)
            if is_uom_day:
                # convert time from hours to days
                amount = round(uom_hour._compute_quantity(amount, company_uom,
                                                          raise_if_failure=False), 2)
            dashboard_values_total_time += amount
            res['dashboard']['time'].update({
                billable_type: amount,
                'total': dashboard_values_total_time
            })

            rate = round(data.get(
                'calculated_hours_invoice') / dashboard_total_hours * 100, 2) \
                if dashboard_total_hours else 0.0
            dashboard_values['rates']['total'] += rate
            dashboard_values_rates_total = dashboard_values['rates']['total']
            res['dashboard']['rates'].update({
                billable_type: rate,
                'total': dashboard_values_rates_total
            })

        repartition_domain = [('project_id', 'in', self.ids),
                              ('employee_id', '!=', False),
                              ('timesheet_invoice_type', '!=', False)]
        cancelled_so_timesheet = self.env['account.analytic.line'].read_group(
            repartition_domain + [('so_line.state', '=', 'cancel')],
            ['employee_id', 'calculated_hours_invoice'],
            ['employee_id'],
            lazy=False)
        repartition_data = self.env['account.analytic.line'].read_group(
            repartition_domain + ['|', ('so_line', '=', False),
                                  ('so_line.state', '!=', 'cancel')],
            ['employee_id', 'timesheet_invoice_type', 'calculated_hours_invoice'],
            ['employee_id', 'timesheet_invoice_type'],
            lazy=False)
        repartition_data += [{**canceled, 'timesheet_invoice_type': 'canceled'}
                             for canceled in cancelled_so_timesheet]
        emp_data = {}
        for data in repartition_data:
            data_timesheet_invoice_type = float_round(
                data.get('calculated_hours_invoice', 0.0),
                precision_rounding=hour_rounding)
            emp_data[int(data.get('employee_id')[0])] = {
                'type': data.get('timesheet_invoice_type'),
                'time': data_timesheet_invoice_type}

        for key, value in res['repartition_employee'].items():
            if emp_data:
                res['repartition_employee'][key].update({
                    emp_data[key]['type']: emp_data[key]['time']})

                res['repartition_employee'][key]['total'] = sum(
                    [value[inv_type] for inv_type in [*billable_types, 'canceled']])

        return res

    def _table_rows_sql_query(self):
        initial_date = fields.Date.from_string(fields.Date.today())
        ts_months = sorted(
            [fields.Date.to_string(initial_date - relativedelta(months=i, day=1))
             for i in range(0, DEFAULT_MONTH_RANGE)])  # M1, M2, M3
        # build query
        query = """
            SELECT
                'timesheet' AS type,
                date_trunc('month', date)::date AS month_date,
                E.id AS employee_id,
                S.order_id AS sale_order_id,
                A.so_line AS sale_line_id,
                SUM(A.calculated_hours_invoice) AS number_hours
            FROM account_analytic_line A
                JOIN hr_employee E ON E.id = A.employee_id
                LEFT JOIN sale_order_line S ON S.id = A.so_line
            WHERE A.project_id IS NOT NULL
                AND A.project_id IN %s
                AND A.date < %s
            GROUP BY date_trunc('month', date)::date, S.order_id, A.so_line, E.id
        """
        last_ts_month = fields.Date.to_string(
            fields.Date.from_string(ts_months[-1]) + relativedelta(months=1))
        query_params = (tuple(self.ids), last_ts_month)
        return query, query_params
