from flectra import api, SUPERUSER_ID

from . import models
from . import controllers

XML_ID = "web_flectra._assets_primary_variables"
SCSS_URL = '/web_flectra/static/src/scss/backend_theme_customizer/colors.scss'


def _uninstall_reset_changes(env):
    env['web_flectra.scss_editor'].reset_values(SCSS_URL, XML_ID)
