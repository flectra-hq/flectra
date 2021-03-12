# Part of flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.exceptions import AccessError
from datetime import datetime
import uuid



TICKET_PRIORITY = [
    ('0', 'All'),
    ('1', 'Low priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _inherit = ['mail.thread.cc',
                'mail.thread',
                'mail.activity.mixin',
                'utm.mixin',
                'portal.mixin',
                'rating.mixin']

    _description = 'Helpdesk Ticket'
    _rec_name = 'issue_name'

    def _default_team_id(self):
        team_id = self.env['helpdesk.team'].search([('visibility_member_ids', 'in', self.env.uid)], limit=1).id
        if not team_id:
            team_id = self.env['helpdesk.team'].search([], limit=1).id
        return team_id

    uid = fields.Many2one('res.users', default=lambda self: self.env.uid)
    issue_name = fields.Char(string='Subject', required=True, index=True, tracking=True)
    team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team', default=_default_team_id, tracking=True)
    help_description = fields.Text()
    active = fields.Boolean(default=True)
    tag_ids = fields.Many2many('helpdesk.tag', string='Tags')
    company_id = fields.Many2one(related='team_id.company_id', string='Company', store=True, readonly=True)
    user_id = fields.Many2one(
        'res.users', string='Assigned to',tracking=True)
    color = fields.Integer(string='Color Index')
    ticket_seq = fields.Char('Sequence', default='New', copy=False)
    priority = fields.Selection([('1', 'Low'), ('2', 'Medium'),
                                 ('3', 'High')], default='1')
    partner_id = fields.Many2one('res.partner', string='Related Partner',
        tracking=True)
    partner_name = fields.Char('Customer Name')
    email = fields.Char(string='Email')
    issue_type_id = fields.Many2one('issue.type', string='Issue Type', store=True)
    start_date = fields.Datetime(
            string='Start Date', default=fields.Datetime.now, tracking=True)
    end_date = fields.Datetime(string='End Date', tracking=True)
    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachments',
            string="Main Attachments", help="Attachment that don't come from message.")
    attachments_count = fields.Integer(compute='_compute_attachments',
                                       string='Add Attachments')
    is_accessible = fields.Boolean('Is Accessible',
                                   compute='_compute_is_accessible')
    is_assigned = fields.Boolean('Is Asigned',
                                 compute='_compute_is_accessible')
    stage_id = fields.Many2one('helpdesk.stage', string='Stage', index=True, tracking=True,
        readonly=False, store=True,copy=False, ondelete='restrict')
    
    feedback = fields.Text('Comment', help="Reason of the rating")

    rating_last_value = fields.Float('Rating Last Value', groups='base.group_user', compute='_compute_rating_last_value', compute_sudo=True, store=True)
    is_rating = fields.Boolean("Is Rating")

    def _merge_ticket_attachments(self, tickets):
        """ Move attachments of given tickets to the current one `self`, and rename
            the attachments having same name than native ones.

        :param tickets: see ``merge_dependences``
        """
        self.ensure_one()

        # return attachments of ticket
        def _get_attachments(ticket_id):
            return self.env['ir.attachment'].search([('res_model', '=', self._name), ('res_id', '=', ticket_id)])

        first_attachments = _get_attachments(self.id)
        # counter of all attachments to move. Used to make sure the name is different for all attachments
        count = 1
        for ticket in tickets:
            attachments = _get_attachments(ticket.id)
            for attachment in attachments:
                values = {'res_id': self.id}
                for attachment_in_first in first_attachments:
                    if attachment.name == attachment_in_first.name:
                        values['name'] = "%s (%s)" % (attachment.name, count)
                count += 1
                attachment.write(values)
        return True

    @api.depends('user_id')
    def _compute_team_id(self):
        """ When changing the user, also set a team_id or restrict team id
        to the ones user_id is member of. """
        for team in self:
            # setting user as void should not trigger a new team computation
            if not team.user_id:
                continue
            user = team.user_id
            if team.team_id and user in team.team_id.member_ids | team.team_id.user_id:
                continue
            team = self.env['helpdesk.team']._get_default_team_id(user_id=user.id)
            team.team_id = team.id

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """

        # remove external users
        if self.env.user.has_group('base.group_portal'):
            self = self.with_context(default_user_id=False)

        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        if self._uid == self.env.ref('base.user_root').id:
            self = self.with_context(default_user_id=False)

        if custom_values is None:
            custom_values = {}
        defaults = {
            'issue_name':  msg_dict.get('subject') or _("No Subject"),
            'email': msg_dict.get('from'),
            'partner_id': msg_dict.get('author_id', False),
            # 'help_description': msg_dict.get('body')
        }
        
        # assign right company
        if 'company_id' not in defaults and 'team_id' in defaults:
            defaults['company_id'] = self.env['helpdesk.team'].browse(defaults['team_id']).company_id.id
        return super(HelpdeskTicket, self).message_new(msg_dict, custom_values=defaults)

    @api.model
    def _default_access_token(self):
        return uuid.uuid4().hex

    access_token = fields.Char('Access Token', default=_default_access_token)
    
    @api.model
    def default_get(self, default_fields):
        vals = super(HelpdeskTicket, self).default_get(default_fields)
        if 'team_id' in vals:
            user_dict = {}  
            team_id = self.env['helpdesk.team'].search(
                [("id", "=", vals['team_id'])])
            if team_id.assignment_method == 'balanced':
                for rec in team_id.member_ids.ids:
                    ticket = self.env['helpdesk.ticket'].search_count(
                        [('team_id', '=', team_id.id), ('user_id', '=', rec)])
                    user_dict.update({rec: ticket})
                temp = min(user_dict.values())
                res = [key for key in user_dict if user_dict[key] == temp]
                vals['user_id'] = res[0]

            if team_id.assignment_method == 'random':
                for member in team_id.member_ids:
                    vals['user_id'] = member.id
        return vals

    @api.onchange('stage_id')
    def onchange_end_date(self):
        if self.stage_id.stage_type == 'done':
            self.end_date = datetime.today()
            mail_id = self.team_id.mail_close_tmpl_id
            if mail_id:
                mail_id.send_mail(res_id=self._origin.id, force_send=True)

    def _creation_subtype(self):
        return self.env.ref('helpdesk_basic.mt_ticket_new')
    
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'user_id' in init_values and self.user_id:
            return self.env.ref('helpdesk_basic.mt_ticket_new')
        elif 'stage_id' in init_values and self.stage_id and \
                self.stage_id.sequence <= 1:
            return self.env.ref('helpdesk_basic.mt_ticket_new')
        elif 'stage_id' in init_values:
            return self.env.ref('helpdesk_basic.mt_ticket_stage')
        return super(HelpdeskTicket, self)._track_subtype(init_values)

    def _message_get_suggested_recipients(self):
        recipients = super(HelpdeskTicket, self)._message_get_suggested_recipients()
        try:
            for ticket in self:
                if ticket.team_id.message_follower_ids:
                    #for follower in ticket.team_id.message_follower_ids:
                    pass
                    # ticket.sudo()._message_add_suggested_recipient(recipients, partner=ticket.partner_id, reason=_('Customer'))
                elif ticket.email:
                    pass
                    # ticket.sudo()._message_add_suggested_recipient(recipients, email=ticket.email, reason=_('Customer Email'))
        except AccessError:  # no read access rights -> just ignore suggested recipients because this imply modifying followers
            pass
        return recipients

    @api.model
    def create(self, values):
        if 'ticket_seq' not in values or values['ticket_seq'] == _('New'):
            values['ticket_seq'] = self.env['ir.sequence'].next_by_code(
                    'helpdesk.ticket') or _('New')
        if values.get('team_id'):
            team = self.team_id.browse(values.get('team_id'))
            values.update(
                {'stage_id': team.stage_ids and team.stage_ids[0].id or False})
        res = super(HelpdeskTicket, self).create(values)
        if not res.stage_id and res.team_id and res.team_id.stage_ids:
            res.stage_id = res.team_id.stage_ids[0]
        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.email = self.partner_id.email

    @api.onchange('team_id')
    def onchange_team_id(self):
        if self.team_id:
            self.stage_id = \
                self.team_id.stage_ids and self.team_id.stage_ids.ids[0]

    def _compute_is_accessible(self):
        has_group = self.env.user.has_group('base.group_no_one')
        for ticket in self:
            if self.env.user.partner_id.id == ticket.partner_id.id or \
                    has_group:
                ticket.is_accessible = True
            if self.env.user.id == ticket.user_id.id or has_group:
                ticket.is_assigned = True

    def _compute_attachments(self):
        for ticket in self:
            attachment_ids = self.env['ir.attachment'].search(
                    [('res_model', '=', ticket._name),
                     ('res_id', '=', ticket.id)])
            ticket.attachments_count = len(attachment_ids.ids)
            ticket.attachment_ids = attachment_ids

    def _auto_rating_request_mail(self):
        ticket_ids = self.env['helpdesk.ticket'].search([])
        for ticket in ticket_ids.filtered(
                lambda r: r.stage_id.stage_type == 'done' and r.team_id.is_rating == True):
            template = self.env.ref('helpdesk_basic.ticket_rating_mail_template')
            if ticket.is_rating != True:
                template.send_mail(res_id=ticket.id, force_send=True)
            ticket.is_rating = True
