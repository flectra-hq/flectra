# -*- coding: utf-8 -*-
# Copyright 2016, 2019 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os
from flectra import api, models, fields

XML_ID = "web_flectra._assets_primary_variables"
SCSS_URL = '/web_flectra/static/src/scss/backend_theme_customizer/colors.scss'

class ResCompany(models.Model):

    _inherit = 'res.company'

    theme_menu_style = fields.Selection([
        ('sidemenu', 'Side Menu'),
        ('apps', 'Top Menu')], string="Menu Style", default="sidemenu")
    theme_font_name = fields.Selection([
        ('Rubik', 'Rubik'),
        ('sans-serif', 'sans-serif')], string="Select Font", default='Rubik')
    theme_color_brand = fields.Char("Theme Brand Color", default="#009efb")
    theme_background_color = fields.Char("Theme Background Color", default="#f2f7fb")
    theme_sidebar_color = fields.Char("Theme Sidebar Color", default="#212529")
    dashboard_background = fields.Binary(attachment=True)

    def set_values(self):
        print('here I am')
        variables = [
            'theme-brand-primary',
            'theme-brand-background-color',
            'theme-root-font-family',
            'theme-sidebar-color',
        ]
        colors = self.env['web_flectra.scss_editor'].get_values(
            SCSS_URL, XML_ID, variables
        )
        colors_changed = []
        colors_changed.append(self.theme_color_brand != colors['theme-brand-primary'])
        colors_changed.append(self.theme_background_color != colors['theme-brand-background-color'])
        colors_changed.append(self.theme_font_name != colors['theme-root-font-family'])
        colors_changed.append(self.theme_sidebar_color != colors['theme-sidebar-color'])
        if(any(colors_changed)):
            variables = [
                {'name': 'theme-brand-primary', 'value': self.theme_color_brand or "#009efb"},
                {'name': 'theme-brand-background-color', 'value': self.theme_background_color or "#f2f7fb"},
                {'name': 'theme-root-font-family', 'value': self.theme_font_name or "Rubik"},
                {'name': 'theme-sidebar-color', 'value': self.theme_sidebar_color or "#212529"},
            ]
            print(variables)
            self.env['web_flectra.scss_editor'].replace_values(
                SCSS_URL, XML_ID, variables
            )

    @api.model
    def get_values(self):
        res = super(ResCompany, self).get_values()
        variables = [
            'theme-brand-primary',
            'theme-brand-background-color',
            'theme-root-font-family',
            'theme-sidebar-color',
        ]
        colors = self.env['web_flectra.scss_editor'].get_values(
            SCSS_URL, XML_ID, variables
        )
        res.update({
            'theme_color_brand': colors['theme-brand-primary'],
            'theme_background_color': colors['theme-brand-background-color'],
            'theme_font_name': colors['theme-root-font-family'],
            'theme_sidebar_color': colors['theme-sidebar-color'],
        })
        return res
