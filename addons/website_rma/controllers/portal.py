# -*- coding: utf-8 -*-
# Part of Odoo,Flectra. See LICENSE file for full copyright and licensing
# details.


from flectra import http
from flectra.http import request, route
from flectra.addons.portal.controllers.portal import CustomerPortal, pager as \
    portal_pager


class CustomerPortal(CustomerPortal):

    @http.route()
    def home(self, **kw):
        response = super(CustomerPortal, self).home(**kw)
        request_count = request.env['rma.request'].sudo().search_count(
            [('state', 'in', ['draft', 'confirmed', 'rma_created',
                              'replacement_created'])])
        response.qcontext.update({
            'request_count': request_count
        })
        return response

    def _order_get_page_view_values(self, order, access_token, **kwargs):
        values = super(CustomerPortal, self)._order_get_page_view_values(
            order, access_token, **kwargs)
        reason_ids = request.env['return.reason'].sudo().search([])
        return_ids = request.env['rma.request'].sudo().search([
            ('sale_order_id', '=', order.id)])
        values.update({
            'reasons': reason_ids,
            'return_ids': return_ids,
        })
        return values

    @http.route(['/my/request', '/my/request/page/<int:page>'], type='http',
                auth="user", website=True)
    def portal_my_requet(self, page=1, date_begin=None, date_end=None,
                         sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        ReturnRequest = request.env['rma.request']
        domain = [
            ('state', 'in', ['draft', 'confirmed', 'rma_created',
                             'replacement_created'])
        ]
        request_count = ReturnRequest.search_count(domain)
        pager = portal_pager(
            url="/my/request",
            url_args={},
            total=request_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        requests = ReturnRequest.sudo().search(domain,
                                               limit=self._items_per_page,
                                               offset=pager['offset'])
        request.session['my_requests_history'] = requests.ids[:100]

        values.update({
            'date': date_begin,
            'requests': requests.sudo(),
            'page_name': 'return_request',
            'pager': pager,
            'archive_groups': '',
            'default_url': '/my/request',
            'searchbar_sortings': '',
            'sortby': sortby,
        })
        return request.render("website_rma.portal_my_requests", values)

    @http.route(['/my/request/<int:return_req>'], type='http',
                auth="public",
                website=True)
    def portal_request_page(self, return_req=None, access_token=None, **kw):
        req = request.env['rma.request'].sudo().browse(return_req)
        values = {
                'return_request': req,
            }
        return request.render("website_rma.portal_request_page", values)

    @http.route(['/return/request'], type='http', auth="public",
                website=True, csrf=False)
    def add_return_request(self, **kw):
        is_replacement = False
        if 'is_replacement_check' in kw and kw['is_replacement_check'] == 'on':
            is_replacement = True
        sale_order = request.env['sale.order'].browse(int(kw['order_id']))
        request_id = request.env['rma.request'].sudo().create({
            'partner_id': kw['partner_id'],
            'sale_order_id': kw['order_id'],
            'team_id': sale_order.team_id and sale_order.team_id.id or False,
            'type': 'web_return_replace',
            'is_website': True,
            'is_replacement': is_replacement,
            'rma_line': [(0, 0, {
                'product_id': kw['product_id'],
                'uom_id': kw['uom_id'],
                'qty_return': kw['quantity'],
                'reason_id': kw['reason'],
                'qty_delivered': kw['qty_delivered'],
                'remark': kw['remark'],
            })
            ],
        })
        request_id.rma_line.write({'rma_id': request_id.id})
        request.session['request_last_return_id'] = request_id.id
        return request.redirect('/return/confirmation')

    @http.route(['/return/confirmation'], type='http', auth="public",
                website=True)
    def return_confirmation(self, **post):
        return_request_id = request.session.get('request_last_return_id')
        if return_request_id:
            return_request = request.env['rma.request'].sudo().browse(
                return_request_id)
            return request.render("website_rma.return_confirmation",
                                  {'return_req_id': return_request})
        else:
            return request.redirect('/shop')

    @route(['/sale/order/pdf/<int:order_id>'], type='http', auth="public",
           website=True)
    def portal_sale_order_report(self, order_id, access_token=None, **kw):
        pdf = request.env.ref('sale.action_report_saleorder'
                              ).sudo().render_qweb_pdf([order_id])[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)
