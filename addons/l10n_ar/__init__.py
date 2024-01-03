# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from . import models
from . import report
from . import demo
from flectra import api, SUPERUSER_ID

def load_translations(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('l10n_ar.l10nar_ri_chart_template').process_coa_translations()
