# Part of Flectra. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    FlectraHQ Inc.
#    Copyright (C) 2017-TODAY FlectraHQ Inc(<https://www.flectrahq.com>).
#
##############################################################################

import json

from flectra import http
from flectra.http import request


class GoogleDriveAuth(http.Controller):

    @http.route('/google_drive/authentication', type='http', auth="public")
    def gdrive_oauth2callback(self, **kw):
        state = json.loads(kw['state'])
        backup_config = (request.env['db.backup.configure'].
                         sudo().browse(state.get('backup_config_id')))
        backup_config.get_gdrive_tokens(kw.get('code'))
        url_return = state.get('url_return')
        return request.redirect(url_return)
