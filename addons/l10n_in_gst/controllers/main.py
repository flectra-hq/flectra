# Part of Flectra See LICENSE file for full copyright and licensing details.

from datetime import datetime

import pytz
from flectra import http, _
from flectra.http import request
from flectra.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ExportExcel(http.Controller):
    @http.route('/l10n_in_gst/export_excel', type='http', auth='user')
    def get_report(self, **kwargs):
        uid = request.session.uid
        gst_report_obj = request.env['gst.report'].sudo(uid)
        data = {
            'from_date': kwargs['from_date'],
            'to_date': kwargs['to_date'],
            'company_id': int(kwargs['company_id']),
            'year': kwargs['year'],
            'month': kwargs['month'],
            'summary_type': kwargs['summary_type'],
        }

        utc_tz = pytz.timezone('UTC')
        tz = pytz.timezone(
            request.env.user.tz) if request.env.user.tz else pytz.utc

        def utc_to_local_zone(naive_datetime):
            utc_dt = utc_tz.localize(naive_datetime,
                                     is_dst=False)
            return utc_dt.astimezone(tz)

        create_date = datetime.strptime(
            datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            DEFAULT_SERVER_DATETIME_FORMAT)
        company_id = request.env['res.company'].browse(int(data['company_id']))
        gst_file_name = ''
        if data['summary_type'] == 'gstr1':
            gst_file_name = _('GSTR-1')
        elif data['summary_type'] == 'gstr2':
            gst_file_name = _('GSTR-2')
        filename = gst_file_name + _('_%s_%s-%s_%s.xlsx') % (
            company_id.vat, datetime.today().strftime("%B"),
            data['year'],
            utc_to_local_zone(create_date).strftime(
                "%d/%m/%Y %H:%M:%S"))

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition',
                 'attachment; filename=' + filename + ';')
            ]
        )
        gst_report_obj.print_report(data, 1, response)
        return response
