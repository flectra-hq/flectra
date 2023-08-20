# coding: utf-8
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
from flectra import models, fields, api, _
from flectra.osv import expression
from flectra.addons.web.controllers.main import clean_action
import json


class Task(models.Model):
    _inherit = 'project.task'
    _description = "Project Task"

    timesheet_invoice_type = fields.Selection([
        ('billable_time', 'Billed on Timesheets'),
        ('billable_fixed', 'Billed at a Fixed price'),
        ('non_billable', 'Non Billable Tasks'),
        ('non_billable_timesheet', 'Non Billable Timesheet'),
        ('non_billable_project', 'No task found')],
        string="Billable Type")
    invoicable_id = fields.Many2one('hr_timesheet_invoice.factor',
                                    string="Invoiceable(%)")
    total_computed_hours = fields.Float(compute="_compute_total_calculated_hours",
                                        help="Time spent on this task,"
                                             " excluding its sub-tasks.")

    @api.onchange('project_id')
    def _compute_timesheet_invoice_type(self):
        values = {
            'timesheet_invoice_type': self.project_id.timesheet_invoice_type,
            'invoicable_id': self.project_id.invoicable_id,
        }
        self.update(values)

    @api.depends('timesheet_ids.unit_amount')
    def _compute_total_calculated_hours(self):
        for task in self:
            task.total_computed_hours = round(sum(
                task.timesheet_ids.mapped('calculated_hours_invoice')), 2)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _description = "Account Analytic Line"

    invoicable_id = fields.Many2one('hr_timesheet_invoice.factor', string="Invoiceable",
                                    readonly=False)
    timesheet_invoice_type = fields.Selection([
        ('billable_time', 'Billed on Timesheets'),
        ('billable_fixed', 'Billed at a Fixed price'),
        ('non_billable', 'Non Billable Tasks'),
        ('non_billable_timesheet', 'Non Billable Timesheet'),
        ('non_billable_project', 'No task found')],
        string="Billable Type", compute=False)
    task_id = fields.Many2one(
        'project.task', 'Task', compute='_compute_task_id',
        store=True, readonly=False, index=True,
        domain="[('company_id', '=', company_id),"
               " ('project_id.allow_timesheets', '=', True),"
               " ('project_id', '=?', project_id)]")

    @api.onchange('task_id')
    def _onchange_timesheet_ids(self):
        values = {
            'timesheet_invoice_type': self.task_id.timesheet_invoice_type,
            'invoicable_id': self.task_id.invoicable_id,
        }
        self.update(values)

    def _timesheet_postprocess_values(self, values):
        res = super(AccountAnalyticLine, self)._timesheet_postprocess_values(values)
        result = {id_: {} for id_ in self.ids}
        sudo_self = self.sudo()
        if any(field_name in values for field_name in ['calculated_hours_invoice',
                                                       'employee_id', 'account_id']):
            for timesheet in sudo_self:
                cost = timesheet.employee_id.timesheet_cost or 0.0
                amount = -timesheet.calculated_hours_invoice * cost
                amount_converted = timesheet.employee_id.currency_id._convert(
                    amount, timesheet.account_id.currency_id, self.env.company,
                    timesheet.date)
                result[timesheet.id].update({
                    'amount': amount_converted,
                })
        res.update(result)
        return result


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sales Order'

    @api.depends('timesheet_ids', 'company_id.timesheet_encode_uom_id')
    def _compute_timesheet_total_duration(self):
        for sale_order in self:
            timesheets = sale_order.timesheet_ids if self.user_has_groups(
                'hr_timesheet.group_hr_timesheet_approver') \
                else sale_order.timesheet_ids.filtered(
                lambda t: t.user_id.id == self.env.uid)
            total_time = 0.0
            for timesheet in timesheets.filtered(lambda t: not t.non_allow_billable):
                # Timesheets may be stored in a different unit of measure,
                # so first we convert all of them to the reference unit
                total_time += timesheet.calculated_hours_invoice * timesheet. \
                    product_uom_id.factor_inv
            # Now convert to the proper unit of measure
            total_time *= sale_order.timesheet_encode_uom_id.factor
            sale_order.timesheet_total_duration = total_time


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sales Order Line'

    def _get_delivered_quantity_by_analytic(self, additional_domain):
        res = super(SaleOrderLine, self)._get_delivered_quantity_by_analytic(
            additional_domain)
        domain = expression.AND([[('so_line', 'in', self.ids)], additional_domain])
        data = self.env['account.analytic.line'].read_group(
            domain,
            ['so_line', 'calculated_hours_invoice', 'product_uom_id'],
            ['product_uom_id', 'so_line'], lazy=False
        )
        for item in data:
            res.update({
                int(item['so_line'][0]): item['calculated_hours_invoice']
            })
        return res


class Project(models.Model):
    _inherit = 'project.project'
    _description = "Project of Project"

    invoicable_id = fields.Many2one('hr_timesheet_invoice.factor',
                                    string="Invoiceable(%)")
    timesheet_invoice_type = fields.Selection([
        ('billable_time', 'Billed on Timesheets'),
        ('billable_fixed', 'Billed at a Fixed price'),
        ('non_billable', 'Non Billable Tasks'),
        ('non_billable_timesheet', 'Non Billable Timesheet'),
        ('non_billable_project', 'No task found')],
        string="Billable Type")
    total_calculated_timesheet_time = fields.Integer(
        compute='_compute_calculated_timesheet_time',
        help="Total number of time (in the proper UoM) recorded in the project,"
             " rounded to the unit.")

    @api.depends('timesheet_ids')
    def _compute_calculated_timesheet_time(self):
        total_time = 0.0
        for project in self:
            for timesheet in project.timesheet_ids:
                # Timesheets may be stored in a different unit of measure, so first
                # we convert all of them to the reference unit
                total_time += timesheet.calculated_hours_invoice * timesheet. \
                    product_uom_id.factor_inv
            # Now convert to the proper unit of measure set in the settings
            total_time *= project.timesheet_encode_uom_id.factor
            project.total_calculated_timesheet_time = int(round(total_time))

    def _plan_get_stat_button(self):
        res = super(Project, self)._plan_get_stat_button()
        ts_tree = self.env.ref('hr_timesheet.hr_timesheet_line_tree')
        ts_form = self.env.ref('hr_timesheet.hr_timesheet_line_form')
        if self.env.company.timesheet_encode_uom_id == self.env.ref(
                'uom.product_uom_day'):
            timesheet_labels = [_('Calculated'), _('Days')]
        else:
            timesheet_labels = [_('Calculated'), _('Hours')]
        res.append({
            'name': timesheet_labels,
            'count': sum(self.mapped('total_calculated_timesheet_time')),
            'icon': 'fa fa-calendar',
            'action': _to_action_data(
                'account.analytic.line',
                domain=[('project_id', 'in', self.ids)],
                views=[(ts_tree.id, 'list'), (ts_form.id, 'form')])
        })
        return res


def _to_action_data(model=None,
                    *, action=None, views=None, res_id=None, domain=None, context=None):
    # pass in either action or (model, views)
    if action:
        assert model is None and views is None
        act = clean_action(action.read()[0], env=action.env)
        model = act['res_model']
        views = act['views']
    # FIXME: search-view-id, possibly help?
    descr = {
        'data-model': model,
        'data-views': json.dumps(views),
    }
    if context is not None:  # otherwise copy action's?
        descr['data-context'] = json.dumps(context)
    if res_id:
        descr['data-res-id'] = res_id
    elif domain:
        descr['data-domain'] = json.dumps(domain)
    return descr
