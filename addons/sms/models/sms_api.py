# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models
from flectra.exceptions import UserError
from flectra.addons.iap.models import iap

DEFAULT_ENDPOINT = 'https://www.flectrahq.com'


class SmsApi(models.AbstractModel):
    _name = 'sms.api'

    @api.model
    def _send_sms(self, numbers, message):
        """ Send sms
        """
        account = self.env['iap.account'].get('sms')
        params = {
            'account_token': account.account_token,
            'numbers': numbers,
            'message': message,
        }
        endpoint = self.env['ir.config_parameter'].sudo().get_param('sms.endpoint', DEFAULT_ENDPOINT)
        r = iap.jsonrpc(endpoint + '/iap/message_send', params=params)
        return True
