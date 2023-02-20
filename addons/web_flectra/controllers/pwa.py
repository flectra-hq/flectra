from flectra.http import Controller, request, route, send_file, Response
from flectra.modules import get_resource_path

from io import BytesIO

import base64
import json
import logging
import json

_logger = logging.getLogger(__name__)


class ProgressiveWebApp(Controller):
    def _get_pwa_config(self, company_id):
        return request.env['pwa.config'].sudo().search([('pwa_company_id', '=', int(company_id))], limit=1)

    def _get_asset_urls(self, asset_xml_id):
        qweb = request.env["ir.qweb"].sudo()
        assets = qweb._get_asset_nodes(asset_xml_id, {}, True, True)
        urls = []
        for asset in assets:
            if asset[0] == "link":
                urls.append(asset[1]["href"])
            if asset[0] == "script":
                urls.append(asset[1]["src"])
        return urls

    def _get_manifest(self, company_id):
        config = self._get_pwa_config(company_id)
        if config:
            icons = []
            manifest = {
                "start_url": "/web",
                "scope": "/web",
            }
            if config.pwa_name:
                manifest.update({
                    'name': config.pwa_name
                })
            if config.pwa_short_name:
                manifest.update({
                    'short_name': config.pwa_short_name
                })
            if config.pwa_background_color:
                manifest.update({
                    'background_color': config.pwa_background_color
                })
            if config.pwa_theme_color:
                manifest.update({
                    'theme_color': config.pwa_theme_color
                })
            if config.pwa_display:
                manifest.update({
                    'display': config.pwa_display
                })
            if config.pwa_icon_128:
                icons.append({
                    'src': '/pwa/icon/128/%s' % str(company_id),
                    'type': "image/png",
                    'sizes': "128x128",
                })
            if config.pwa_icon_192:
                icons.append({
                    'src': '/pwa/icon/192/%s' % str(company_id),
                    'type': "image/png",
                    'sizes': "192x192",
                })
            if config.pwa_icon_512:
                icons.append({
                    'src': '/pwa/icon/512/%s' % str(company_id),
                    'type': "image/png",
                    'sizes': "512x512",
                })
            if len(icons) == 0:
                icons = [{
                    "src": "/web_flectra/static/img/icons/icon-512x512.png",
                    "type": "image/png",
                    "sizes": "512x512",
                    }]
            manifest.update({'icons': icons})
            return json.dumps(manifest)
        else:
            file = get_resource_path('web_flectra', 'static', 'src', 'manifest.json')
            response = send_file(file, filename='manifest.json', mimetype='application/json')
            return response

    def _get_icon(self, icon_size, company_id):
        config = self._get_pwa_config(company_id)
        if config:
            if icon_size == 128:
                icon = config.pwa_icon_128
            elif icon_size == 192:
                icon = config.pwa_icon_192
            elif icon_size == 512:
                icon = config.pwa_icon_512
            if icon:
                icon = BytesIO(base64.b64decode(icon))
                return request.make_response(icon.read(), [('Content-Type', 'image/png')])
        return False

    @route("/service-worker.js", type="http", auth="public")
    def service_worker(self):
        qweb = request.env["ir.qweb"].sudo()
        urls = []
        urls.extend(self._get_asset_urls("web.assets_common"))
        urls.extend(self._get_asset_urls("web.assets_backend"))
        urls.extend(self._get_asset_urls("web.assets_backend_prod_only"))
        urls.extend(self._get_asset_urls("web.assets_common_minimal_js"))
        urls.extend(self._get_asset_urls("web.assets_frontend_minimal_js"))
        urls.extend(self._get_asset_urls("web.assets_common_lazy"))
        urls.extend(self._get_asset_urls("web.assets_frontend_lazy"))
        version_list = []
        for url in urls:
            if len(url.split("/")) >= 3:
                version_list.append(url.split("/")[3])
        urls.extend([
            '/web/static/lib/fontawesome/fonts/fontawesome-webfont.woff2?v=4.7.0',
            '/web/static/src/img/favicon.ico',
            '/web_flectra/static/src/img/icons/icon-128x128.png',
            '/web_flectra/static/src/img/icons/icon-144x144.png',
            '/web_flectra/static/src/img/icons/icon-152x152.png',
            '/web_flectra/static/src/img/icons/icon-192x192.png',
            '/web_flectra/static/src/img/icons/icon-256x256.png',
            '/web_flectra/static/src/img/icons/icon-512x512.png',
        ])
        cache_version = "-".join(version_list)
        mimetype = "text/javascript;charset=utf-8"
        content = qweb._render(
            "web_flectra.service_worker",
            {"pwa_cache_name": cache_version, "pwa_files_to_cache": urls},
        )
        return request.make_response(content, [("Content-Type", mimetype)])

    @route(["/manifest.json/<int:company_id>","/manifest.json"], type="http", auth="public")
    def manifest(self, **kwargs):
        if not 'company_id' in kwargs or not kwargs['company_id']:
            company_id = 1
        else:
            company_id = kwargs.get('company_id')
        return self._get_manifest(company_id)

    @route('/pwa/icon/128/<int:company_id>', type='http', auth="public")
    def icon_128(self, **kwargs):
        return self._get_icon(128, kwargs.get('company_id'))

    @route('/pwa/icon/192/<int:company_id>', type='http', auth="public")
    def icon_192(self, **kwargs):
        return self._get_icon(192, kwargs.get('company_id'))

    @route('/pwa/icon/512/<int:company_id>', type='http', auth="public")
    def icon_512(self, **kwargs):
        return self._get_icon(512, kwargs.get('company_id'))

    @route('/onesignal/fetch', type='json', auth='none', csrf=False,
           methods=['GET', 'POST'])
    def fetch_onesignal_app_id(self, **kwargs):
        """Method To Fetch One Signal App ID"""
        val = {
            'ONESIGNAL_APP_ID': request.env['ir.config_parameter'].sudo().get_param('onesignal_app_id'),
        }

        return val

    @route('/onesignal/register', type='json', auth='none', csrf=False,
           methods=['GET', 'POST'])
    def register_onesignal_device(self, **kwargs):
        """Method To Register One Signal Device ID In User"""
        if kwargs.get('user_id'):
            user = request.env['res.users'].sudo().search([
                ('id', '=', int(kwargs.get('user_id')))])
            if kwargs.get('userdevice_id'):
                user.update({
                    'onesignal_device_id': kwargs.get('userdevice_id')
                })
                return True
        return False
