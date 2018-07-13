# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details

import logging
from flectra import api, fields, models, _

_logger = logging.getLogger(__name__)


# This is a nasty hack, targeted for V11 only
class IrModel(models.Model):
    _inherit = 'ir.model'

    @api.multi
    def unlink(self):
        self.env.cr.execute("DELETE FROM ir_model_fields WHERE name='website_id'")
        self.env.cr.execute("DELETE FROM res_config_settings WHERE website_id IS NOT NULL")
        return super(IrModel, self).unlink()


class IrModelData(models.Model):
    _inherit = 'ir.model.data'

    # Overriding Method
    @api.model
    def _update(self, model, module, values, xml_id=False, store=True,
                noupdate=False, mode='init', res_id=False):
        # records created during module install should not display the messages of OpenChatter
        self = self.with_context(install_mode=True)
        current_module = module

        if xml_id and ('.' in xml_id):
            assert len(xml_id.split('.')) == 2, _(
                "'%s' contains too many dots. XML ids should not contain dots ! These are used to refer to other modules data, as in module.reference_id") % xml_id
            module, xml_id = xml_id.split('.')

        action = self.browse()
        record = self.env[model].browse(res_id)

        if xml_id:
            self._cr.execute("""SELECT imd.id, imd.res_id, md.id, imd.model, imd.noupdate
                                    FROM ir_model_data imd LEFT JOIN %s md ON (imd.res_id = md.id)
                                    WHERE imd.module=%%s AND imd.name=%%s""" % record._table,
                             (module, xml_id))
            results = self._cr.fetchall()
            for imd_id, imd_res_id, real_id, imd_model, imd_noupdate in results:
                # In update mode, do not update a record if it's ir.model.data is flagged as noupdate
                if mode == 'update' and imd_noupdate:
                    return imd_res_id
                if not real_id:
                    self.clear_caches()
                    self._cr.execute('DELETE FROM ir_model_data WHERE id=%s',
                                     (imd_id,))
                    record = record.browse()
                else:
                    assert model == imd_model, "External ID conflict, %s already refers to a `%s` record," \
                                               " you can't define a `%s` record with this ID." % (
                                               xml_id, imd_model, model)
                    action = self.browse(imd_id)
                    record = record.browse(imd_res_id)

        if action and record:
            # Set ``is_cloned`` to ``False``
            if values.get('type') == 'qweb' and not values.get('is_cloned'):
                values.update({'is_cloned': False})

            record.write(values)
            action.sudo().write({'date_update': fields.Datetime.now()})

        elif record:
            record.write(values)
            if xml_id:
                for parent_model, parent_field in record._inherits.items():
                    self.sudo().create({
                        'name': xml_id + '_' + parent_model.replace('.', '_'),
                        'model': parent_model,
                        'module': module,
                        'res_id': record[parent_field].id,
                        'noupdate': noupdate,
                    })
                self.sudo().create({
                    'name': xml_id,
                    'model': model,
                    'module': module,
                    'res_id': record.id,
                    'noupdate': noupdate,
                })

        elif mode == 'init' or (mode == 'update' and xml_id):
            existing_parents = set()  # {parent_model, ...}
            if xml_id:
                for parent_model, parent_field in record._inherits.items():
                    xid = self.sudo().search([
                        ('module', '=', module),
                        ('name', '=',
                         xml_id + '_' + parent_model.replace('.', '_')),
                    ])
                    # XML ID found in the database, try to recover an existing record
                    if xid:
                        parent = self.env[xid.model].browse(xid.res_id)
                        if parent.exists():
                            existing_parents.add(xid.model)
                            values[parent_field] = parent.id
                        else:
                            xid.unlink()

            record = record.create(values)
            if xml_id:
                # To add an external identifiers to all inherits model
                inherit_models = [record]
                while inherit_models:
                    current_model = inherit_models.pop()
                    for parent_model_name, parent_field in current_model._inherits.items():
                        inherit_models.append(self.env[parent_model_name])
                        if parent_model_name in existing_parents:
                            continue
                        self.sudo().create({
                            'name': xml_id + '_' + parent_model_name.replace(
                                '.', '_'),
                            'model': parent_model_name,
                            'module': module,
                            'res_id': record[parent_field].id,
                            'noupdate': noupdate,
                        })
                        existing_parents.add(parent_model_name)
                self.sudo().create({
                    'name': xml_id,
                    'model': model,
                    'module': module,
                    'res_id': record.id,
                    'noupdate': noupdate
                })
                if current_module and module != current_module:
                    _logger.warning(
                        "Creating the ir.model.data %s in module %s instead of %s.",
                        xml_id, module, current_module)

        if xml_id and record:
            self.loads[(module, xml_id)] = (model, record.id)
            for parent_model, parent_field in record._inherits.items():
                parent_xml_id = xml_id + '_' + parent_model.replace('.', '_')
                self.loads[(module, parent_xml_id)] = (
                parent_model, record[parent_field].id)

        return record.id

    @api.model
    def _process_end(self, modules):
        super(IrModelData, self)._process_end(modules)
        ir_ui_view = self.env['ir.ui.view']
        ir_model_data = self.env['ir.model.data']

        default_website = self.env['website'].search([
            ('is_default_website', '=', True)])
        for cus_view in ir_ui_view.search([('customize_show', '=', True),
                                           ('website_id', '=', False),
                                           '|', ('active', '=', False),
                                           ('active', '=', True)]):
            if default_website:
                cus_view.write({'website_id': default_website.id})

        for website in self.env['website'].search(
                [('is_default_website', '=', False)]):
            for view in ir_ui_view.search(
                    [('website_id', '=', default_website.id),
                     ('customize_show', '=', True), ('is_cloned', '=', False),
                     '|', ('active', '=', False), ('active', '=', True)]):
                if not ir_ui_view.search(
                        [('key', '=', view.key +
                            '_' + website.website_code),
                         '|', ('active', '=', False), ('active', '=', True)]):
                    new_cus_view = view.copy({
                        'is_cloned': True,
                        'key': view.key + '_' + website.website_code,
                        'website_id': website.id
                    })
                    new_inherit_id = ir_ui_view.search(
                        [('key', '=', new_cus_view.inherit_id.key +
                          '_' + website.website_code),
                         '|', ('active', '=', False), ('active', '=', True)])
                    if new_cus_view.inherit_id and new_inherit_id:
                        new_cus_view.write({
                            'inherit_id': new_inherit_id.id,
                        })
                    model_data_id = ir_model_data.create({
                        'model': view.model_data_id.model,
                        'name': view.model_data_id.name +
                        '_' + website.website_code,
                        'res_id': new_cus_view.id,
                        'module': view.model_data_id.module,
                    })
                    new_cus_view.write({
                        'model_data_id': model_data_id
                    })
