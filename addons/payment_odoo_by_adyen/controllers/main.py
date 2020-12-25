# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import json
import logging
import pprint

from flectra import http
from flectra.http import request

_logger = logging.getLogger(__name__)


class FlectraByAdyenController(http.Controller):
    _notification_url = '/payment/flectra_adyen/notification'

    @http.route('/payment/flectra_adyen/notification', type='json', auth='public', csrf=False)
    def flectra_adyen_notification(self):
        data = json.loads(request.httprequest.data)
        _logger.info('Beginning Flectra by Adyen form_feedback with data %s', pprint.pformat(data)) 
        if data.get('authResult') not in ['CANCELLED']:
            request.env['payment.transaction'].sudo().form_feedback(data, 'flectra_adyen')
