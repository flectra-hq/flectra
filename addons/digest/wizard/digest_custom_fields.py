# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.exceptions import ValidationError
from lxml import etree
from flectra.tools.safe_eval import test_python_expr
import xml.etree.ElementTree as ET


class DigestCustomFields(models.TransientModel):
    _name = 'digest.custom.fields'

    field_name = fields.Char('Field Name', default='x_kpi_', required=True)
    label_name = fields.Char('Label Name', required=True)
    new_group_name = fields.Char('Group Name')
    ttype = fields.Selection([
        ('integer', 'Integer'),
        ('monetary', 'Monetary')],
        string='Field Type', required=True, default='integer')
    compute = fields.Text(string='Compute', groups='base.group_system')
    compute_field_name = fields.Char(
        compute='_compute_get_field_name', string='Compute Field Name')
    available_group_name = fields.Selection(
        '_get_group_name', string='Available Group')
    position = fields.Selection([
        ('before', 'Before'),
        ('after', 'After'),
        ('inside', 'Inside')],
        string='Position')
    model_id = fields.Many2one(
        'ir.model', string='Model')
    model_name = fields.Char(related='model_id.model', string='Model Name')
    model_domain = fields.Char(string='Domain', oldname='domain', default=[])
    model_real = fields.Char(compute='_compute_model', string='Real Model')
    related_date_field_id = fields.Many2one('ir.model.fields', 'Date')

    @api.onchange('compute_field_name', 'model_id', 'model_domain',
                  'related_date_field_id')
    def onchange_compute_field_name(self):
        data = """for record in self:
  start, end, company = record._get_kpi_compute_parameters()
  """
        domain = self.model_domain
        date = self.related_date_field_id
        domain_values = """[["%s", ">=", start], ["%s", "<", end]]""" % (
            date.name or '', date.name or '')
        if domain != '[]':
            domain += domain_values
            domain = domain.replace("][", ",")
        else:
            domain = domain_values
        data += "record['%s'] = self.env['%s'].search_count(%s)" % (
            self.compute_field_name, self.model_real or '', domain) + "\n\n"
        self.compute = data

    @api.depends('model_id')
    def _compute_model(self):
        for record in self:
            if record.model_id:
                record.model_real = record.model_name or 'res.users'

    def _get_group_name(self):
        digest_view_id = self.env.ref('digest.digest_digest_view_form').id
        view_ids = self.env['ir.ui.view'].search([
            ('inherit_id', 'child_of', digest_view_id)])
        group_value = {}
        for view_id in view_ids:
            root = ET.fromstring(view_id.arch_base)
            for group_name in root.iter('group'):
                if group_name.attrib.get('name', False):
                    group_key = \
                        str(view_id.id) + '_' + str(group_name.attrib['name'])
                    if not group_name.attrib.get('string', False):
                        group_string = group_name.attrib['name'][4:].capitalize()
                    else:
                        group_string = group_name.attrib['string']
                    group_value.update({
                        group_key: group_string})
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
                raise ValidationError(_("Custom fields must have a name that "
                                        "starts with 'x_kpi_'!"))
            try:
                models.check_pg_name(field.field_name)
            except ValidationError:
                msg = _("Field names can only contain characters, digits and"
                        " underscores (up to 63).")
                raise ValidationError(msg)

    def add_new_fields(self):
        model_id = self.env['ir.model'].search([
            ('model', '=', 'digest.digest')])
        ir_model_fields_obj = self.env['ir.model.fields']

        first_field_name = self.field_name
        values = {
            'model_id': model_id.id,
            'ttype': 'boolean',
            'name': first_field_name,
            'field_description': self.label_name,
            'model': 'digest.digest'
        }

        compute_values = {
            'model_id': model_id.id,
            'ttype': self.ttype,
            'name': self.field_name + '_value',
            'field_description': self.label_name + ' Value',
            'model': 'digest.digest',
            'depends': first_field_name,
            'compute': self.compute
        }

        try:
            ir_model_fields_obj.create(values)
            ir_model_fields_obj.create(compute_values)
        except Exception as e:
            raise ValidationError(e)

    def field_arch(self):
        xpath = etree.Element('xpath')
        name = self.available_group_name and self.available_group_name.split(
            '_', 1)[1] or "kpis"
        expr = '//' + 'group' + '[@name="' + name + '"]'
        xpath.set('expr', expr)
        xpath.set('position', self.position)
        field = etree.Element('field')
        field.set('name', self.field_name)
        xpath.set('expr', expr)

        if self.position == 'inside':
            xpath.append(field)
        else:
            group = etree.Element('group')
            group.set('name', 'x_kpi_' + self.new_group_name.replace(" ", "_"))
            group.set('string', self.new_group_name)
            group.append(field)
            xpath.append(group)

        return etree.tostring(xpath).decode("utf-8")

    @api.multi
    def action_add_customize_digest(self):
        self.add_new_fields()
        arch = '<?xml version="1.0"?>' + str(self.field_arch())
        view_id = self.available_group_name and \
            self.available_group_name.split('_', 1)[0] or False
        vals = {
            'type': 'form',
            'model': 'digest.digest',
            'inherit_id':
                view_id or self.env.ref('digest.digest_digest_view_form').id,
            'mode': 'extension',
            'arch_base': arch,
            'name': 'x_kpi_' + self.field_name + "_customization",
        }
        ir_model = self.env['ir.model'].search([
            ('model', '=', 'digest.digest')])
        if hasattr(ir_model, 'module_id'):
            vals.update({'module_id': ir_model.module_id.id})
        self.env['ir.ui.view'].sudo().create(vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
