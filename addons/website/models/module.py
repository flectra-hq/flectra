from flectra import api, fields, models, _
from flectra.exceptions import Warning


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    website_ids = fields.One2many('website', 'website_theme_id',
                                  string='Website', readonly=True)

    @api.multi
    def button_immediate_install(self):
        for app in self:
            if app.category_id and (
                            app.category_id.name == 'Theme'
                    or app.category_id.parent_id.name == 'Theme') and \
                    not app.website_ids:
                raise Warning(_('You are trying to install Theme module!\n'
                                'As Flectra will support multi-website so, '
                                'please install theme in specific website.\n'
                                'Go to...\n'
                                '- Menu: Website/Configuration/Settings\n'
                                '- Select website & its theme & Save it.'))
        return super(IrModuleModule, self).button_immediate_install()
