# -*- coding: utf-8 -*-
# Copyright 2016, 2019 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os
from flectra import api, models, fields
import base64

XML_ID = "web_flectra._assets_primary_variables"
SCSS_URL = '/web_flectra/static/src/scss/backend_theme_customizer/colors.scss'


class ResCompany(models.Model):

    _inherit = 'res.company'

    theme_menu_style = fields.Selection([
        ('sidemenu', 'Side Menu'),
        ('apps', 'Top Menu')], string="Menu Style", default="apps")
    theme_font_name = fields.Selection([
        ('Rubik', 'Rubik'),
        ('sans-serif', 'sans-serif'),
        ('poppins', 'Poppins'),
        ('lato', 'Lato'),
        ('merriweather', 'Merriweather'),
        ('montserrat', 'Montserrat'),
        ('opensans', 'OpenSans'),
        ('playfairdisplay', 'PlayfairDisplay'),
        ('google-font', 'Google Font')], string="Select Font", default='Rubik')
    google_font = fields.Char('Google Font', default='Roboto')
    theme_color_brand = fields.Char("Theme Brand Color", default="#009efb")
    theme_background_color = fields.Char("Theme Background Color", default="#f2f7fb")
    theme_sidebar_color = fields.Char("Theme Sidebar Color", default="#212529")
    dashboard_background = fields.Binary(attachment=True)

    def write(self, vals):
        res = super(ResCompany, self).write(vals)
        if self:
            for rec in self:
                content = """
                    $theme-brand-primary: %s;
                    $theme-brand-background-color: %s;
                    $theme-root-font-family: %s;
                    $theme-sidebar-color: %s;
                    $backend-google-font: %s;
                """ % (
                    rec.theme_color_brand,
                    rec.theme_background_color,
                    rec.theme_font_name,
                    rec.theme_sidebar_color,
                    rec.google_font,
                )
                IrAttachment = self.env["ir.attachment"]
                url = "/web_flectra/static/src/scss/backend_theme_customizer/colors.scss"

                search_attachment = IrAttachment.sudo().search([
                    ('url', '=', url),
                ], limit=1)

                datas = base64.b64encode((content or "\n").encode("utf-8"))
                if search_attachment:
                    search_attachment.sudo().write({"datas": datas})

                else:
                    new_attach = {
                        "name": "Back Theme Settings scss File",
                        "type": "binary",
                        "mimetype": "text/scss",
                        "datas": datas,
                        "url": url,
                        "public": True,
                        "res_model": "ir.ui.view",
                    }

                    IrAttachment.sudo().create(new_attach)

                self.env["ir.qweb"].clear_caches()
        return res

    @api.model
    def get_values(self):
        res = super(ResCompany, self).get_values()
        variables = [
            'theme-brand-primary',
            'theme-brand-background-color',
            'theme-root-font-family',
            'theme-sidebar-color',
            'google-font'
        ]
        colors = self.env['web_flectra.scss_editor'].get_values(
            SCSS_URL, XML_ID, variables
        )
        res.update({
            'theme_color_brand': colors['theme-brand-primary'],
            'theme_background_color': colors['theme-brand-background-color'],
            'theme_font_name': colors['theme-root-font-family'],
            'theme_sidebar_color': colors['theme-sidebar-color'],
            'google_font': colors['google-font'],
        })
        return res
