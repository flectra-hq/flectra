# -*- coding: utf-8 -*-
from flectra import http
from flectra.http import request
from flectra.addons.web.controllers.main import _serialize_exception
from flectra.tools import html_escape

import json


class BarcodeController(http.Controller):

    @http.route(['/stock/barcode/'], type='http', auth='user')
    def a(self, debug=False, **k):
        if not request.session.uid:
            return http.local_redirect('/web/login?redirect=/stock/barcode/')

        return request.render('stock.barcode_index')


class StockReportController(http.Controller):

    @http.route('/stock/<string:output_format>/<string:report_name>/<int:report_id>', type='http', auth='user')
    def report(self, output_format, report_name, token, report_id=False, **kw):
        uid = request.session.uid
        domain = [('create_uid', '=', uid)]
        stock_traceability = request.env['stock.traceability.report'].sudo(uid).search(domain, limit=1)
        line_data = json.loads(kw['data'])
        try:
            if output_format == 'pdf':
                response = request.make_response(
                    stock_traceability.with_context(active_id=report_id).get_pdf(line_data),
                    headers=[
                        ('Content-Type', 'application/pdf'),
                        ('Content-Disposition', 'attachment; filename=' + 'stock_traceability' + '.pdf;')
                    ]
                )
                response.set_cookie('fileToken', token)
                return response
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Flectra Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
