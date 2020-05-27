# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import http
from flectra.http import request
from flectra.addons.portal.controllers.portal import CustomerPortal
from flectra.addons.portal.controllers.portal import get_records_pager
from flectra.addons.portal.controllers.portal import pager as portal_pager
import copy

class HelpdeskTicket(http.Controller):

    @http.route(['/helpdesk-form'], type='http', auth='user', website=True)
    def helpdesk_issue_form(self, **post):
        issue_type = request.env['issue.type'].sudo().search([])
        team_ids = request.env['helpdesk.team'].sudo().search([])
        assign_to_ids = request.env['res.users'].sudo().search([])
        post.update({
            'asignee': request.env.user,
            'email': request.env.user.partner_id.email or '',
            'partner_id': request.env.user.partner_id.id,
            'issue_type': issue_type,
            'team_ids': team_ids,
            'assign_to_ids': assign_to_ids,
        })
        return request.render('website_helpdesk.helpdesk_form', post)

    @http.route(['/issue-submitted'], type='http', auth='user',
                website=True)
    def issue_submitted(self, **post):
        attachment_obj = request.env['ir.attachment']
        post.update({'user_id': request.session.uid})
        post_data = copy.deepcopy(post)
        for k in post:
            if k=='file' or 'file_data_' in k:
                post_data.pop(k)
        ticket = request.env['helpdesk.ticket'].sudo().create(post_data)
        helpdesk_team = request.env["helpdesk.team"].sudo().search([('issue_type_ids', 'in',
                                                  ticket.issue_type_id.id)])
        for team_id in helpdesk_team:
            ticket.update({
                'team_id': team_id.id,
                'stage_id': request.env.ref('helpdesk_basic.helpdesk_stage_draft')
            })
            if request.env.user.partner_id:
                ticket.partner_id = request.env.user.partner_id or False
        values = {'ticket_seq': ticket.ticket_seq}
        file_data = [key for key in post if 'file_data_' in key]
        for name in file_data:
            attachment_obj.sudo().create(
                {'name': name,
                 'res_model': 'helpdesk.ticket',
                 'res_id': ticket,
                 'res_name': post.get('name'),
                 'datas': post.get(name)})
        return request.render("website_helpdesk.issue_submitted", values)

    @http.route(
        ['/helpdesk-form/issue_description/<model("issue.type"):issue_type_id>'
         ], type='json', auth="user", methods=['POST'], website=True)
    def issue_description(self, issue_type_id, **kw):
        domain = []
        if issue_type_id:
            domain.append(('id', '=', issue_type_id.id))
        return dict(
            description=request.env['issue.type'].sudo().search(
                domain, limit=1).mapped('reporting_template'))


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        ticket = request.env['helpdesk.ticket'].sudo().search_count(
            [('user_id', '=', request.env.user.id)])

        values.update({
            'ticket_count': ticket,

        })
        return values

    @http.route(['/my/ticket', '/my/ticket/page/<int:page>'], type='http',
                auth="user", website=True)
    def portal_my_ticket(self, page=1, ticket_id=None, **kw):
        domain = [('user_id', '=', request.session.uid)]
        ticket_count = request.env['helpdesk.ticket'].sudo().search_count(domain)
        pager = portal_pager(
            url="/my/tickets",
            url_args={},
            total=ticket_count,
            page=page,
            step=self._items_per_page
        )
        tickets = request.env['helpdesk.ticket'].sudo().search(
            domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_tickets_history'] = tickets.ids[:100]
        vals = {
            'ticket': tickets,
            'user': request.env.user,
            'pager': pager,

        }
        return request.render("website_helpdesk.my_tickets", vals)

    @http.route(['/my/ticket/<int:ticket_id>'], type='http',
                auth="user", website=True)
    def list_my_tickets(self, ticket_id=None, **kw):
        values = self._prepare_portal_layout_values()
        ticket = request.env['helpdesk.ticket'].sudo().search(
            [('id', '=', ticket_id)])
        rating = request.env['rating.rating'].sudo().search(
            [('res_model', '=', 'helpdesk.ticket'),
             ('res_id', '=', ticket.id),
             ('write_uid', '=', request.session.uid)])
        display_rating = False
        if ticket.stage_id and ticket.stage_id.stage_type == 'done':
            display_rating = True
        values.update({'ticket': ticket, 'rating': rating,
                       'priority': int(ticket.priority),
                       'display_rating': display_rating})
        history = request.session.get('my_tickets_history', [])
        values.update(get_records_pager(history, ticket))
        return request.render("website_helpdesk.portal_my_ticket", values)
