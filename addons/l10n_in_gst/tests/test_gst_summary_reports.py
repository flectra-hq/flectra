from datetime import datetime
from dateutil.relativedelta import relativedelta
from .test_gst_common import TestGSTCommon


class TestGSTSummaryReports(TestGSTCommon):
    def test_00_gstr_summary_reports(self):
        # call open_document
        gst_report_obj = self.env['gst.report'].sudo(self.env.uid)
        options = {'object': 'account.invoice', 'id': self.account_invoice_b2b}
        gst_report_obj.open_document(options)

        data = {
            'from_date': (datetime.today() - relativedelta(months=1))
            .strftime('%Y-%m-01'),
            'to_date': (datetime.today() - relativedelta(months=1))
            .strftime('%Y-%m-28'),
            'company_id': self.env.user.company_id.id,
            'year': datetime.today().year,
            'month': datetime.today().month,
            'template': 'ViewSummary',
            'data_action_method': 'get_gstr_summary'
        }

        # call summary for GSTR1
        data.update({'summary_type': 'gstr1'})
        gst_report_obj.get_gstr_summary(data)
        # print excel report for gstr 1 report
        gst_report_obj.write_data_into_sheets({'form': data})

        # call summary for GSTR2
        data.update({'summary_type': 'gstr2'})
        gst_report_obj.get_gstr_summary(data)
        # print excel report for gstr 2 report
        gst_report_obj.write_data_into_sheets({'form': data})
