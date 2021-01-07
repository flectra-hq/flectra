from flectra import api, fields, models, modules, tools, _

class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    license = fields.Selection(selection_add=[('FPL-1', 'Flectra Proprietary License v1.0'),
                                              ('FEEL-1', 'Flectra Enterprise Edition License v1.0'),
                                              ])
