# Part of flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_project = fields.Boolean("Use Projects")
    use_website_form = fields.Boolean("Website Form")
    module_helpdesk_forum = fields.Boolean('Helpdesk Forum')
    module_helpdesk_project_ext = fields.Boolean('Helpdesk project')
    module_website_helpdesk = fields.Boolean('Helpdesk Website')
    module_helpdesk_elearning = fields.Boolean('E-Learning')
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            use_project=get_param('helpdesk_basic.use_project'),
            use_website_form=get_param('helpdesk_basic.use_website_form')
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('helpdesk_basic.use_project', self.use_project)
        set_param('helpdesk_basic.use_website_form', self.use_website_form)