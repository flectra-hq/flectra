# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.exceptions import ValidationError, UserError
from lxml import etree
from flectra.tools.safe_eval import test_python_expr


class DigestCustomFields(models.TransientModel):
    _name = 'digest.custom.fields'


    DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: Flectra Environment on which the action is triggered
#  - model: Flectra Model of the record on which the action is triggered; is a void recordset
#  - record: record on which the action is triggered; may be be void
#  - records: recordset of all records on which the action is triggered in multi-mode; may be void
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - Warning: Warning Exception to use with raise
# To return an action, assign: action = {...}\n\n\n\n"""


    # field = fields.Many2one('ir.model.fields', domain="[('model_id', '=', 'digest.digest'), ('name', 'ilike', 'x_kpi'), ('depends', '=', False)]")
    # compute_field = fields.Many2one('ir.model.fields', domain="[('model_id', '=', 'digest.digest'), ('name', 'ilike', 'x_kpi'), ('depends', '!=', False)]")
        
    field_name = fields.Char('Field Name', default='x_kpi_', required=True)
    label_name = fields.Char('Label Name', required=True)
    group_name = fields.Char('Group Name', required=True)
    ttype = fields.Selection([('integer', 'Integer'), ('monetary', 'Monetary')], string='Field Type', required=True)
    # compute = fields.Text(help="Code to compute the value of the field.\n"
    #                            "Iterate on the recordset 'self' and assign the field's value:\n\n"
    #                            "    for record in self:\n"
    #                            "        record['size'] = len(record.name)\n\n"
    #                            "Modules time, datetime, dateutil are available.")


    compute = fields.Text(string='Python Code', groups='base.group_system',
                       default=DEFAULT_PYTHON_CODE,
                       help="Write Python code that the action will execute. Some variables are "
                            "available for use; help about pyhon expression is given in the help tab.")

    compute_field_name = fields.Char(compute='_compute_get_field_name', string='Compute Field Name')

    @api.constrains('compute')
    def _check_python_code(self):
        for record in self.sudo().filtered('compute'):
            msg = test_python_expr(expr=record.compute.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    @api.depends('field_name')
    def _compute_get_field_name(self):
        for record in self:
            if record.field_name:
                record.compute_field_name = record.field_name + '_value'

    @api.constrains('field_name')
    def _check_name(self):
        for field in self:
            if not field.field_name.startswith('x_kpi_'):
                raise ValidationError(_("Custom fields must have a name that starts with 'x_kpi_' !"))
            try:
                models.check_pg_name(field.field_name)
            except ValidationError:
                msg = _("Field names can only contain characters, digits and underscores (up to 63).")
                raise ValidationError(msg)

    def add_new_fields(self):
        model_id = self.env['ir.model'].search([('model', '=', 'digest.digest')])
        ir_model_fields_obj = self.env['ir.model.fields']

        first_field_name = self.field_name
        values = {
            'model_id': model_id.id,
            'ttype': 'boolean',
            'name': first_field_name,
            'field_description': self.label_name,
            'model': 'digest.digest'
        }
        ir_model_fields_obj.create(values)

        values = {
            'model_id': model_id.id,
            'ttype': self.ttype,
            'name': self.field_name + '_value',
            'field_description': self.label_name + ' Value',
            'model': 'digest.digest',
            'depends': first_field_name,
            'compute': self.compute
        }
        print("====values=======", values)
        ir_model_fields_obj.create(values)

    def field_arch(self):
        xpath = etree.Element('xpath')
        xpath_type = "group"
        name = "kpi_general"
        position = "after"
        xpath_field = self.field_name
        expr = '//' + xpath_type + '[@name="' + name + '"][not(ancestor::field)]'
        xpath.set('expr', expr)
        xpath.set('position', position)
        if position == 'after' or position == 'before' or position == 'inside':
            expr = '//' + xpath_type + '[@name="' + name + '"][not(ancestor::field)]'
            group = etree.Element('group')
            group.set('string', self.group_name)
            field = etree.Element('field')
            field.set('name', xpath_field)
            xpath.set('expr', expr)
            group.append(field)
            xpath.append(group)
        return etree.tostring(xpath).decode("utf-8")

    @api.multi
    def action_customize_digest(self):
        self.add_new_fields()
        arch = '<data>' + str(self.field_arch()) + '</data>'
        print("====arch=======", arch)
        vals = {
            'type': 'form',
            'model': 'digest.digest',
            'inherit_id': self.env.ref('digest.digest_digest_view_form').id,
            'mode': 'extension',
            'arch_base': arch,
            'name': 'x_kpi_' + self.field_name + "_Customization",
        }
        ir_model = self.env['ir.model'].search([('model', '=', 'digest.digest')])
        if hasattr(ir_model, 'module_id'):
            vals.update({'module_id': ir_model.module_id.id})
        self.env['ir.ui.view'].sudo().create(vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

