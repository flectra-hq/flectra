# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import logging
from ast import literal_eval

from flectra import api, fields, models, _
from flectra.exceptions import AccessDenied, AccessError, Warning

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _default_website(self):
        return self.env['website'].search([], limit=1)

    # FIXME: Set website_id to ondelete='cascade' in master
    website_id = fields.Many2one('website', string="website", default=_default_website, required=True)
    website_name = fields.Char('Website Name', related='website_id.name')
    language_ids = fields.Many2many(related='website_id.language_ids', relation='res.lang')
    language_count = fields.Integer(string='Number of languages', compute='_compute_language_count', readonly=True)
    default_lang_id = fields.Many2one(string='Default language', related='website_id.default_lang_id', relation='res.lang', required=True)
    default_lang_code = fields.Char('Default language code', related='website_id.default_lang_code')
    google_analytics_key = fields.Char('Google Analytics Key', related='website_id.google_analytics_key')
    google_management_client_id = fields.Char('Google Client ID', related='website_id.google_management_client_id')
    google_management_client_secret = fields.Char('Google Client Secret', related='website_id.google_management_client_secret')

    cdn_activated = fields.Boolean('Use a Content Delivery Network (CDN)', related='website_id.cdn_activated')
    cdn_url = fields.Char(related='website_id.cdn_url')
    cdn_filters = fields.Text(related='website_id.cdn_filters')

    favicon = fields.Binary('Favicon', related='website_id.favicon')
    # Set as global config parameter since methods using it are not website-aware. To be changed
    # when multi-website is implemented
    google_maps_api_key = fields.Char(string='Google Maps API Key')
    has_google_analytics = fields.Boolean("Google Analytics")
    has_google_analytics_dashboard = fields.Boolean("Google Analytics in Dashboard")
    has_google_maps = fields.Boolean("Google Maps")
    auth_signup_uninvited = fields.Selection([
        ('b2b', 'On invitation (B2B)'),
        ('b2c', 'Free sign up (B2C)'),
    ], string='Customer Account')
    website_theme_id = fields.Many2one(
        'ir.module.module', string='Theme',
        related='website_id.website_theme_id',
        help='Choose theme for current website.')

    # Unique theme per Website for now ;)
    # @todo Flectra:
    # Do enable support for same theme in multiple website
    @api.onchange('website_theme_id')
    def onchange_theme_id(self):
        if (self.website_id.id not in self.website_theme_id.website_ids.ids) \
                and (self.website_theme_id and
                     self.website_theme_id.website_ids):
            warning = {
                'title': 'Warning',
                'message': _('Selected theme is already active in '
                             'different website.')}
            self.website_theme_id = False
            return {'warning': warning}

    @api.onchange('has_google_analytics')
    def onchange_has_google_analytics(self):
        if not self.has_google_analytics:
            self.has_google_analytics_dashboard = False
        if not self.has_google_analytics:
            self.google_analytics_key = False

    @api.onchange('has_google_analytics_dashboard')
    def onchange_has_google_analytics_dashboard(self):
        if not self.has_google_analytics_dashboard:
            self.google_management_client_id = False
            self.google_management_client_secret = False

    @api.onchange('language_ids')
    def _onchange_language_ids(self):
        # If current default language is removed from language_ids
        # update the default_lang_id
        if self.language_ids and self.default_lang_id not in self.language_ids:
            self.default_lang_id = self.language_ids[0]

    @api.depends('language_ids')
    def _compute_language_count(self):
        for config in self:
            config.language_count = len(self.language_ids)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            auth_signup_uninvited='b2c' if get_param('auth_signup.allow_uninvited', 'False').lower() == 'true' else 'b2b',
            has_google_analytics=get_param('website.has_google_analytics'),
            has_google_analytics_dashboard=get_param('website.has_google_analytics_dashboard'),
            has_google_maps=get_param('website.has_google_maps'),
            google_maps_api_key=get_param('google_maps_api_key', default=''),
        )
        return res

    def set_values(self):
        if not self.user_has_groups('website.group_website_designer'):
            raise AccessDenied()
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('auth_signup.allow_uninvited', repr(self.auth_signup_uninvited == 'b2c'))
        set_param('website.has_google_analytics', self.has_google_analytics)
        set_param('website.has_google_analytics_dashboard', self.has_google_analytics_dashboard)
        set_param('website.has_google_maps', self.has_google_maps)
        set_param('google_maps_api_key', (self.google_maps_api_key or '').strip())

    @api.multi
    def open_template_user(self):
        action = self.env.ref('base.action_res_users').read()[0]
        action['res_id'] = literal_eval(self.env['ir.config_parameter'].sudo().get_param('auth_signup.template_user_id', 'False'))
        action['views'] = [[self.env.ref('base.view_users_form').id, 'form']]
        return action

    @api.model
    def _get_classified_fields(self):
        res = super(ResConfigSettings, self)._get_classified_fields()
        if 'website_theme_id' in dir(self):
            ir_module = self.env['ir.module.module']
            install_theme_lst = []
            uninstall_theme_lst = []
            install_theme_lst.append(self.website_theme_id)
            theme_un = ir_module.sudo().search(
                ['|', ('category_id.name', '=', 'Theme'),
                 ('category_id.parent_id.name', '=', 'Theme')]
            )
            for theme in theme_un:
                if not theme.website_ids and len(theme.website_ids.ids) < 1:
                    uninstall_theme_lst.append(theme)
            res.update({
                'install_theme': install_theme_lst,
                'uninstall_theme': uninstall_theme_lst
            })
        return res

    # Overriding Method
    @api.multi
    def execute(self):
        self.ensure_one()

        # Multi Website: Do not allow more than 1 website as default website
        if self.env['website'].search_count(
                [('is_default_website', '=', True)]) > 1:
            raise Warning(
                _('You can define only one website as default one.\n'
                  'More than one websites are not allowed '
                  'as default website.'))

        if not self.env.user._is_superuser() and not \
                self.env.user.has_group('base.group_system'):
            raise AccessError(_("Only administrators can change the settings"))

        self = self.with_context(active_test=False)
        classified = self._get_classified_fields()

        # default values fields
        IrDefault = self.env['ir.default'].sudo()
        for name, model, field in classified['default']:
            if isinstance(self[name], models.BaseModel):
                if self._fields[name].type == 'many2one':
                    value = self[name].id
                else:
                    value = self[name].ids
            else:
                value = self[name]
            IrDefault.set(model, field, value)

        # group fields: modify group / implied groups
        for name, groups, implied_group in classified['group']:
            if self[name]:
                groups.write({'implied_ids': [(4, implied_group.id)]})
            else:
                groups.write({'implied_ids': [(3, implied_group.id)]})
                implied_group.write({'users': [(3, user.id) for user in
                                               groups.mapped('users')]})

        # other fields: execute method 'set_values'
        # Methods that start with `set_` are now deprecated
        for method in dir(self):
            if method.startswith('set_') and method is not 'set_values':
                _logger.warning(_('Methods that start with `set_` '
                                  'are deprecated. Override `set_values` '
                                  'instead (Method %s)') % method)
        self.set_values()

        # module fields: install/uninstall the selected modules
        to_install = []
        to_upgrade = self.env['ir.module.module']
        to_uninstall_modules = self.env['ir.module.module']
        lm = len('module_')
        for name, module in classified['module']:
            if self[name]:
                to_install.append((name[lm:], module))
            else:
                if module and module.state in ('installed', 'to upgrade'):
                    to_uninstall_modules += module

        if 'install_theme' in classified and 'uninstall_theme' in classified:
            for theme in classified['install_theme']:
                if theme:
                    to_install.append((theme.name, theme))
                if theme.state == 'installed':
                    to_upgrade += theme
            for theme in classified['uninstall_theme']:
                if theme and theme.state in ('installed', 'to upgrade'):
                    to_uninstall_modules += theme

        if to_uninstall_modules:
            to_uninstall_modules.button_immediate_uninstall()

        if to_upgrade:
            to_upgrade.button_immediate_upgrade()

        self._install_modules(to_install)

        if to_install or to_uninstall_modules:
            # After the uninstall/install calls, the registry and environments
            # are no longer valid. So we reset the environment.
            self.env.reset()
            self = self.env()[self._name]

        # pylint: disable=next-method-called
        config = self.env['res.config'].next() or {}
        if config.get('type') not in ('ir.actions.act_window_close',):
            return config

        # force client-side reload (update user menu and current view)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
