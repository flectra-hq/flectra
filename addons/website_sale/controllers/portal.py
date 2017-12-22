# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.
from flectra import http
from flectra.http import request
from flectra import tools, _
from flectra.exceptions import AccessError
from flectra.addons.sale.controllers.portal import CustomerPortal
from flectra.addons.account.controllers.portal import PortalAccount


class SaleCustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(SaleCustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        SaleOrder = request.env['sale.order']
        quotation_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of',
             [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'cancel']),
            ('website_id', '=', request.website.id),
        ])
        order_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of',
             [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done']),
            ('website_id', '=', request.website.id),
        ])

        values.update({
            'quotation_count': quotation_count,
            'order_count': order_count,
        })
        return values

    @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http',
                    auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None,
                         sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of',
             [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'cancel']),
            ('website_id', '=', request.website.id),
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = request.website.pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end,
                      'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.search(domain, order=sort_order,
                                      limit=self._items_per_page,
                                      offset=pager['offset'])
        request.session['my_quotes_history'] = quotations.ids[:100]
        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'quote',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/quotes',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_quotations",
                              values)

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http',
                    auth="user", website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None,
                         sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of',
             [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done']),
            ('website_id', '=', request.website.id),
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end,
                      'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.search(domain, order=sort_order,
                                  limit=self._items_per_page,
                                  offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_orders", values)

    @http.route()
    def portal_order_page(self, order=None, access_token=None, **kw):
        order = request.env['sale.order'].browse([order])
        try:
            if order.website_id != request.website:
                raise AccessError('Invalid Order !!')
        except AccessError:
            return request.render("website.403")

        return super(SaleCustomerPortal, self).portal_order_page(order.id,
                                                            access_token, **kw)

    @http.route()
    def portal_order_report(self, order_id, access_token=None, **kw):
        order = request.env['sale.order'].browse([order_id])
        try:
            if order.website_id != request.website:
                raise AccessError('Invalid Order !!')
        except AccessError:
            return request.render("website.403")

        return super(SaleCustomerPortal, self).portal_order_report(order_id,
                                                                 access_token,
                                                                 **kw)


class AccountCustomerPortal(PortalAccount):

    def _prepare_portal_layout_values(self):
        values = super(AccountCustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        invoice_count = request.env['account.invoice'].search_count([
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('message_partner_ids', 'child_of',
             [partner.commercial_partner_id.id]),
            ('state', 'in', ['open', 'paid', 'cancel']),
            ('website_id', '=', request.website.id),
        ])

        values['invoice_count'] = invoice_count
        return values

    @http.route()
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None,
                           sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        AccountInvoice = request.env['account.invoice']

        domain = [
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('message_partner_ids', 'child_of',
             [partner.commercial_partner_id.id]),
            ('state', 'in', ['open', 'paid', 'cancelled']),
            ('website_id', '=', request.website.id),
        ]

        searchbar_sortings = {
            'date': {'label': _('Invoice Date'), 'order': 'date_invoice desc'},
            'duedate': {'label': _('Due Date'), 'order': 'date_due desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('account.invoice', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # count for pager
        invoice_count = AccountInvoice.search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin,
                      'date_end': date_end,
                      'sortby': sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = AccountInvoice.search(domain, order=order,
                                         limit=self._items_per_page,
                                         offset=pager['offset'])
        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/invoices',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("account.portal_my_invoices", values)

    @http.route()
    def portal_my_invoice_detail(self, invoice_id, access_token=None, **kw):
        invoice = request.env['account.invoice'].browse(invoice_id)
        try:
            if invoice.website_id != request.website:
                raise AccessError('Invalid Invoice !!')
        except AccessError:
            return request.render("website.403")

        return super(PortalAccount, self).portal_my_invoice_detail(invoice_id, access_token,**kw)

    @http.route()
    def portal_my_invoice_report(self, invoice_id, **kw):
        invoice = request.env['account.invoice'].browse(invoice_id)
        try:
            if invoice.website_id != request.website:
                raise AccessError('Invalid Invoice !!')
        except AccessError:
            return request.render("website.403")

        return super(PortalAccount, self).portal_my_invoices_report(invoice_id,
                                                                    **kw)
