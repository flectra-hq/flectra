
import base64
from flectra.http import Controller, request, route
from werkzeug.utils import redirect
DEFAULT_IMAGE = \
    '/web_flectra/static/src/img/application-switcher-bg-dark.png'


class DashboardBackground(Controller):

    @route(['/app-menu-bg'], type='http', auth='user', website=False)
    def dashboard(self, **post):
        user = request.env.user
        company = user.company_id
        if company.menu_bg_image:
            image = base64.b64decode(company.menu_bg_image)
        else:
            return redirect(DEFAULT_IMAGE)

        return request.make_response(
            image, [('Content-Type', 'image')])
        
    @route('/theme/get/menus', type='json', auth='user')
    def get_theme_menus(self, **post):
        return request.env['ir.ui.menu'].sudo().load_menus_root()

    @route(['/web/backend_theme_customizer/read'], type='json', website=True, auth="user")
    def customizer_read(self):
        user = request.env['res.users'].sudo().search(
            [('id', '=', request.env.user.id)])
        company = user.company_id
        return {
            'user_settings': {
                'chatter_position': user.chatter_position,
                'dark_mode': user.dark_mode
            },
            'company_settings': {
                'theme_menu_style': company.theme_menu_style,
                'theme_font_name': company.theme_font_name,
                'theme_color_brand': company.theme_color_brand,
                'theme_background_color': company.theme_background_color,
                'theme_sidebar_color': company.theme_sidebar_color,
                'preloader_option': company.preloader_option,
                'google_font': company.google_font
            }
        }

    @route(['/web/backend_theme_customizer/write'], type='json', website=True, auth="user", methods=['POST'])
    def customizer_write(self, **post):
        user = request.env['res.users'].sudo().search(
            [('id', '=', request.env.user.id)])
        company = user.company_id
        if user.has_group('base.group_erp_manager') and 'company_settings' in post:
            result = {}
            company_settings = post['company_settings']
            for entry in company_settings:
                if entry in ["theme_menu_style", "theme_font_name", "preloader_option", "theme_color_brand",
                             "theme_background_color", "theme_sidebar_color","google_font"]:
                    result.update({entry: company_settings[entry]})
            company.update(result)
        elif 'user_settings' in post:
            result = {}
            user_settings = post['user_settings']
            for entry in user_settings:
                if entry == 'chatter_position':
                    result.update({entry: user_settings[entry]})
                elif entry == 'dark_mode':
                    result.update({entry: user_settings[entry]})
            user.update(result)
        return True
