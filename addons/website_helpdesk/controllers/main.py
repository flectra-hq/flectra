# Part of flectra See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from flectra import http, _
from flectra.http import request
from flectra.addons.portal.controllers.portal import CustomerPortal
from flectra.addons.portal.controllers.portal import get_records_pager
from flectra.addons.portal.controllers.portal import pager as portal_pager
from flectra.exceptions import AccessError, MissingError
import copy
from flectra.osv import expression

class HelpdeskTicket(http.Controller):

    @http.route(['/helpdesk-form'], type='http', auth='user', website=True)
    def helpdesk_issue_form(self, **post):
        issue_type = request.env['issue.type'].sudo().search([])
        team_ids = request.env['helpdesk.team'].sudo().search([])
        assign_to_ids = request.env['res.users'].sudo().search([])
        config = request.env['res.config.settings'].sudo().search([])
        get_param = request.env['ir.config_parameter'].sudo().get_param
        website_form = get_param('helpdesk_basic.use_website_form')
        post.update({
            'asignee': request.env.user,
            'email': request.env.user.partner_id.email or '',
            'partner_id': request.env.user.partner_id.id,
            'issue_type': issue_type,
            'assign_to_ids': assign_to_ids,
        })
        if website_form:
            return request.render('website_helpdesk.helpdesk_form', post)
        else:
            return request.render('website_helpdesk.helpdesk_web_form')

    @http.route(['/issue-submitted'], type='http', auth='user',
                website=True)
    def issue_submitted(self, **post):
        if 'issue_type_id' in post:
            is_id = post['issue_type_id']
            type_id = int(is_id)
            team = request.env['helpdesk.team'].sudo().search([('issue_type_ids', '=', type_id)])
        attachment_obj = request.env['ir.attachment']
        post_data = copy.deepcopy(post)
        for k in post:
            if k=='file' or 'file_data_' in k:
                post_data.pop(k)
        ticket = request.env['helpdesk.ticket'].sudo().create(post_data)
        for rec in team:
            if rec:
                ticket.update(
                    {'team_id': rec[0],
                     'stage_id': rec.stage_ids[0].id or False})
                user_dict = {}
                for member in ticket.team_id.member_ids:
                    if rec.assignment_method == 'balanced':
                        tickets = request.env['helpdesk.ticket'].sudo().search_count([('team_id', '=', rec.id),('user_id', '=', member.id)])
                        user_dict.update({member: tickets})
                        temp = min(user_dict.values())
                        res = [key for key in user_dict if user_dict[key] == temp]
                        ticket.user_id = res[0]

                    if rec.assignment_method == 'random':
                        ticket.user_id = member.id
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
            help_description=request.env['issue.type'].sudo().search(
                domain, limit=1).mapped('reporting_template'))


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters=None):
        values = super(CustomerPortal, self)._prepare_home_portal_values(counters)
        user = request.env.user
        ticket = request.env['helpdesk.ticket'].sudo().search_count(['|',
                ('user_id', '=', user.id),('partner_id', '=', user.partner_id.id)])
        values.update({
            'ticket_count': ticket,

        })
        return values

    def _ticket_get_page_view_values(self, ticket, access_token, **kwargs):
        values = {
            'page_name': 'ticket',
            'ticket': ticket,
        }
        return self._get_page_view_values(ticket, access_token, values, 'my_tickets_history', False, **kwargs)

    @http.route(['/my/ticket/<int:ticket_id>'], type='http', auth="user", website=True)
    def portal_my_home_ticket(self, ticket_id=None, access_token=None, **kw):
        try:
            project_sudo = self._document_check_access('helpdesk.ticket', ticket_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._ticket_get_page_view_values(project_sudo, access_token, **kw)
        return request.render("website_helpdesk.portal_my_home_ticket", values)

    def get_search_domain_ticket(self, search, attrib_values):
        domain = []
        if search:
            for srch in search.split(" "):
                domain += [
                    '|',
                    ('issue_name', 'ilike', srch),
                    ('ticket_seq', 'ilike', srch),
                ]
        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]
        return domain


    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http',
                auth="user", website=True)
    def portal_my_ticket(self, page=1, ticket_id=None, sortby=None, filterby=None,
        groupby=None, search=None, search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        domain = []
        searchbar_sortings = {
            'id': {'label': _('Newest'), 'order': 'id desc'},
            'issue_name': {'label': _('Subject'), 'order': 'issue_name asc'},
            'ticket_seq': {'label': _('Sequence'), 'order': 'ticket_seq asc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'draft': {'label': _('Draft'), 'domain': [('stage_id.stage_type', '=', 'draft')]},
            'done': {'label': _('Done'), 'domain': [('stage_id.stage_type', '=', 'done')]},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'ticket_seq': {'input': 'ticket_seq', 'label': _('Search in Sequence No')},
            'issue_name': {'input': 'issue_name', 'label': _('Search in Name')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'stage_id': {'input': 'stage_id', 'label': _('Stage')},
        }
        if not sortby:
            sortby = 'id'

        if not filterby:
            filterby = 'all'

        order = searchbar_sortings[sortby]['order']
        
        if not groupby:
            groupby = 'none'

        if groupby == 'team_id':
            order = "team_id, %s" % order
        elif groupby == 'stage_id':
            order = "stage_id, %s" % order

        user = request.env.user
        domain = ['|',('user_id', '=', user.id),('partner_id', '=', user.partner_id.id)]

        if search and search_in:
            search_domain = []
            if search_in in ('all', 'ticket_seq'):
                search_domain = expression.OR(
                    [search_domain, [('ticket_seq', 'ilike', search)]])
            if search_in in ('all', 'issue_name'):
                search_domain = expression.OR(
                    [search_domain, [('issue_name', 'ilike', search)]])
            domain += search_domain

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])
        domain += self.get_search_domain_ticket(search, attrib_values)

        domain += searchbar_filters[filterby]['domain']
        tickets = request.env['helpdesk.ticket'].sudo().search(domain, order=order)
        
        ticket_count = tickets.sudo().search_count(domain)
        pager = portal_pager(
            url="/my/tickets",
            url_args={'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search_in': search_in, 'search': search},
            total=ticket_count,
            page=page,
            step=self._items_per_page
        )
        request.session['my_tickets_history'] = tickets.ids[:100]
        values.update({
            'tickets': tickets,
            'user': request.env.user,
            'page_name': 'ticket',
            'default_url': '/my/tickets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })

        return request.render("website_helpdesk.my_tickets", values)

    @http.route(['/my/ticket/<int:ticket_id>'], type='http',
                auth="user", website=True)
    def list_my_tickets(self, ticket_id=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
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
                       'page_name': 'ticket',
                       'display_rating': display_rating})
        history = request.session.get('my_tickets_history', [])
        values.update(get_records_pager(history, ticket))
        return request.render("website_helpdesk.portal_my_ticket", values)
