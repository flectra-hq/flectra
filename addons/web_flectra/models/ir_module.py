from flectra import api, fields, models, modules, tools, _
from flectra.osv import expression


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    license = fields.Selection(selection_add=[('FPL-1', 'Flectra Proprietary License v1.0'),
                                              ('FPEL-1', 'Flectra Professional Edition License v1.0'),
                                              ])
    module_type = fields.Selection(selection="_get_selection_app_options", required=False)
    def _get_selection_app_options(self):
        return [('official', 'Official Apps')]

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        domain = expression.AND([domain, [('to_buy', '!=', True)]])
        return super().web_search_read(domain, specification, offset=offset, limit=limit, order=order, count_limit=count_limit)
