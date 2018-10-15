# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models
import xml.etree.ElementTree as ET
from flectra.osv import expression


class DigestCustomRemove(models.TransientModel):
    _name = 'digest.custom.remove'

    remove_type = fields.Selection([
        ('group', 'Group'),
        ('field', 'Field')],
        string='Remove Type')
    field_id = fields.Many2one('ir.model.fields', 'Field', domain=[
        ('model', '=', 'digest.digest'),
        ('required', '=', False),
        ('ttype', '=', 'boolean'),
        ('name', 'ilike', 'x_kpi_')])
    available_group_name = fields.Selection(
        '_get_group_name', string='Available Group')

    def _get_group_name(self):
        digest_view_id = self.env.ref('digest.digest_digest_view_form').id
        view_ids = self.env['ir.ui.view'].search([
            ('inherit_id', 'child_of', digest_view_id)])
        group_value = {}
        for view_id in view_ids:
            root = ET.fromstring(view_id.arch_base)
            for group_name in root.iter('group'):
                if group_name.attrib.get('name', False) \
                    and group_name.attrib.get('string', False) \
                        and group_name.attrib['name'].startswith('x_kpi_'):
                    group_key = \
                        str(view_id.id) + '_' + str(group_name.attrib['name'])
                    group_value.update({
                        group_key: group_name.attrib['string']})
        return [(x) for x in group_value.items()]

    @api.multi
    def action_customize_digest_remove(self):
        ir_model_fields_obj = self.env['ir.model.fields']
        ir_ui_view_obj = self.env['ir.ui.view']
        if self.remove_type == 'group':
            find_view_id = self.available_group_name \
                        and self.available_group_name.split('_', 1)[0] or False
            view_ids = ir_ui_view_obj.search([
                ('inherit_id', 'child_of', int(find_view_id))],
                order="id desc")
            field_list = []
            for view_id in view_ids:
                root = ET.fromstring(view_id.arch_base)
                for child in root.iter('group'):
                    name = child.find('field')
                    if name.attrib and name.attrib.get('name', False):
                        field_list.append(name.attrib.get('name', False))
            field_ids = ir_model_fields_obj.search([
                ('name', 'in', field_list)])
            view_ids.unlink()
            for field_id in field_ids:
                ir_model_fields_obj.search([
                    ('depends', '=', field_id.name)]).unlink()
            field_ids.unlink()
        else:
            domain = expression.OR([('arch_db', 'like', record.name)
                                    ] for record in self.field_id)
            view_ids = ir_ui_view_obj.search(domain)
            for view_id in view_ids:
                root = ET.fromstring(view_id.arch_base)
                for child in root.iter('field'):
                    if child.attrib and child.attrib.get(
                            'name', False) == self.field_id.name:
                        view_id.unlink()
            ir_model_fields_obj.search([
                ('depends', '=', self.field_id.name)]).unlink()
            self.field_id.unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
