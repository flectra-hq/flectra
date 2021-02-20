import logging
from flectra import models, fields, api, _

_logger = logging.getLogger(__name__)


class ProgressiveWebAppConfig(models.Model):
    _name = 'pwa.config'
    _rec_name = 'pwa_name'
    _description = 'Progressive Web App Configuration'

    active = fields.Boolean("Active", default=True)
    pwa_name = fields.Char(
            string='Name',
    )
    pwa_short_name = fields.Char(
            string='Short Name',
    )
    pwa_background_color = fields.Char(
            string="Background Color",
    )
    pwa_theme_color = fields.Char(
            string="Theme Color",
    )
    pwa_icon_128 = fields.Binary(
            string="Icon (128x128)",
    )
    pwa_icon_192 = fields.Binary(
            string="Icon (192x192)",
    )
    pwa_icon_512 = fields.Binary(
            string="Icon (512x512)",
    )
    pwa_display = fields.Selection(
            string='Display',
            selection=[
                ('fullscreen', 'Fullscreen'),
                ('standalone', 'Standalone'),
                ('minimal-ui', 'Minimal UI'),
                ('browser', 'Browser'),
            ],
            help='How the PWA should look like\nFullscreen: Opens the web application without any browser UI and takes up the entirety of the available display area.'
                 '\n\nStandalone: Opens the web app to look and feel like a standalone native app. The app runs in its own window, separate from the browser, and hides standard browser UI elements like the URL bar, etc.'
                 '\n\nMinimal UI: This mode is similar to fullscreen, but provides the user with some means to access a minimal set of UI elements for controlling navigation (i.e., back, forward, reload, etc). Note: Only supported by Chrome on mobile.'
                 '\n\nBrowser: 	A standard browser experience.',
            default='standalone',
    )
    pwa_scope = fields.Char(
            string='Scope',
            help='The scope defines the set of URLs that the browser considers to be within your app, and is used to decide when the user has left the app.',
            default='/',
    )
    pwa_company_id = fields.Many2one(
            'res.company', string="Company", default=lambda self: self.env.user.company_id.id)
