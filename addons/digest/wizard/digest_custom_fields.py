# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.exceptions import ValidationError, UserError
from lxml import etree
from flectra.tools.safe_eval import test_python_expr
import xml.etree.ElementTree as ET


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
# To return an action, assign: action = {...}
for rec in self:
  rec[''] = self.env[''].search([])\n\n\n\n"""


    field_name = fields.Char('Field Name', default='x_kpi_', required=True)
    label_name = fields.Char('Label Name', required=True)
    # group_type = fields.Selection([('new', 'New Group'), ('existing', 'Existing Group')], string='Group Type', required=True)
    new_group_name = fields.Char('Group Name')
    ttype = fields.Selection([('integer', 'Integer'), ('monetary', 'Monetary')], string='Field Type', required=True, default='integer')
    compute = fields.Text(string='Python Code', groups='base.group_system',
                       default=DEFAULT_PYTHON_CODE,
                       help="Write Python code that the action will execute. Some variables are "
                            "available for use; help about pyhon expression is given in the help tab.")

    compute_field_name = fields.Char(compute='_compute_get_field_name', string='Compute Field Name')
    available_group_name = fields.Selection('_get_group_name', string='Available Group')
    position = fields.Selection([('before', 'Before'), ('after', 'After'), ('inside', 'Inside')], string='Position')

    def _get_group_name(self):
        print("=====self=========", self.env.context)
        digest_view_id = self.env.ref('digest.digest_digest_view_form').id
        view_ids = self.env['ir.ui.view'].search([('inherit_id', 'child_of', digest_view_id)])
        group_value = {}
        for view_id in view_ids:
            root = ET.fromstring(view_id.arch_base)
            for group_name in root.iter('group'):
                if group_name.attrib.get('name', False) and group_name.attrib.get('string', False):
                    group_key = str(view_id.id) + '_' + str(group_name.attrib['name'])
                    group_value.update({group_key : group_name.attrib['string']})
        return [(x) for x in group_value.items()]

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
                raise ValidationError(_("Custom fields must have a name that starts with 'x_kpi_'!"))
            # if self.position != 'inside' and not field.new_group_name.startswith('x_kpi_'):
            #     raise ValidationError(_("Group Name must have a name that starts with 'x_kpi_'!"))
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
        ir_model_fields_obj.create(values)

    def field_arch(self):
        xpath = etree.Element('xpath')
        name = self.available_group_name and self.available_group_name.split('_', 1)[1] or "kpis"
        expr = '//' + 'group' + '[@name="' + name + '"]'
        xpath.set('expr', expr)
        xpath.set('position', self.position)

        if self.position == 'inside':
            field = etree.Element('field')
            field.set('name', self.field_name)
            xpath.set('expr', expr)
            xpath.append(field)
        else:
            group = etree.Element('group')
            group.set('name', 'x_kpi_' + self.new_group_name.replace(" ", "_"))
            group.set('string', self.new_group_name)
            field = etree.Element('field')
            field.set('name', self.field_name)
            xpath.set('expr', expr)
            group.append(field)
            xpath.append(group)

        return etree.tostring(xpath).decode("utf-8")

    @api.multi
    def action_add_customize_digest(self):
        self.add_new_fields()
        arch = '<?xml version="1.0"?>' + str(self.field_arch())
        view_id = self.available_group_name and self.available_group_name.split('_', 1)[0] or False
        vals = {
            'type': 'form',
            'model': 'digest.digest',
            'inherit_id': view_id or self.env.ref('digest.digest_digest_view_form').id,
            'mode': 'extension',
            'arch_base': arch,
            'name': 'x_kpi_' + self.field_name + "_customization",
        }
        ir_model = self.env['ir.model'].search([('model', '=', 'digest.digest')])
        if hasattr(ir_model, 'module_id'):
            vals.update({'module_id': ir_model.module_id.id})
        self.env['ir.ui.view'].sudo().create(vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

