# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _description = 'Helpdesk Ticket'

    @api.model
    def _get_default_state(self):
        if self.team_id and self.team_id.stage_ids:
            return self.team_id.stage_ids[0]

    active = fields.Boolean('Active', default=True)
    color = fields.Integer(string='Color Index')
    name = fields.Char('Name', translate=True)
    ticket_seq = fields.Char('Sequence', default='New', copy=False,
                             oldname='sequence')
    priority = fields.Selection([('1', 'Low'), ('2', 'Medium'),
                                 ('3', 'High')], default='1')
    user_id = fields.Many2one('res.users', string='Created By',
                              track_visibility='onchange')
    partner_id = fields.Many2one(
        'res.partner',
        string='Related Partner',
        track_visibility='onchange')
    email = fields.Char(
            string='Email',
            default=lambda s: s.env.user.partner_id.email or False)
    issue_type_id = fields.Many2one('issue.type', string='Issue Type',
                                    track_visibility='onchange')
    team_id = fields.Many2one('helpdesk.team', 'Team',
                              track_visibility='onchange')
    assigned_to_id = fields.Many2one('res.users', string='Assigned To',
                                     track_visibility='onchange')
    tag_ids = fields.Many2many('helpdesk.tag', string='Tag(s)')
    start_date = fields.Datetime(
            string='Start Date', default=fields.Datetime.now,
            track_visibility='onchange')
    end_date = fields.Datetime(
        string='End Date', default=fields.Datetime.now,
        track_visibility='onchange')
    description = fields.Text(string='Description', size=128, translate=True,
                              track_visibility='onchange')
    attachment_ids = fields.One2many(
            'ir.attachment', compute='_compute_attachments',
            string="Main Attachments",
            help="Attachment that don't come from message.")
    attachments_count = fields.Integer(compute='_compute_attachments',
                                       string='Add Attachments')
    is_accessible = fields.Boolean('Is Accessible',
                                   compute='_compute_is_accessible')
    is_assigned = fields.Boolean('Is Accessible',
                                 compute='_compute_is_accessible')
    stage_id = fields.Many2one('helpdesk.stage', string='Stage',
                               default=_get_default_state,
                               track_visibility='onchange')

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'assigned_to_id' in init_values and self.assigned_to_id:
            # assigned -> new
            return 'helpdesk_basic.mt_issue_new'
        elif 'stage_id' in init_values and self.stage_id and \
                self.stage_id.sequence <= 1:  # start stage -> new
            return 'helpdesk_basic.mt_issue_new'
        elif 'stage_id' in init_values:
            return 'helpdesk_basic.mt_issue_stage'
        return super(HelpdeskTicket, self)._track_subtype(init_values)

    def add_followers(self):
        followers = []
        followers.append(self.assigned_to_id.id)
        followers.append(self.user_id.id)
        self.message_subscribe_users(user_ids=followers)

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
        res.add_followers()
        return res

    @api.multi
    def write(self, vals):
        if vals.get('partner_id', False) or vals.get('assigned_to_id', False):
            self.add_followers()
        return super(HelpdeskTicket, self).write(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.email = self.partner_id.email

    @api.onchange('team_id')
    def onchange_team_id(self):
        self.assigned_to_id = False
        if self.team_id:
            self.stage_id = \
                self.team_id.stage_ids and self.team_id.stage_ids.ids[0]
            return {'domain': {
                'assigned_to_id':
                    [('id', 'in', self.team_id.member_ids and
                      self.team_id.member_ids.ids or [])],
                'stage_id':
                    [('id', 'in', self.team_id.stage_ids and
                      self.team_id.stage_ids.ids or [])]
            }}

    @api.onchange('issue_type_id')
    def onchange_issue_type_id(self):
        self.team_id = False
        if self.issue_type_id:
            team = self.env["helpdesk.team"].search([('issue_type_ids', 'in',
                                                      self.issue_type_id.id)])
            for teams in team:
                self.team_id = teams.id
            self.description = self.issue_type_id.reporting_template or ''
            return {'domain': {'team_id': [('issue_type_ids', 'in',
                                            self.issue_type_id.id)]}}

    @api.multi
    def _compute_is_accessible(self):
        has_group = self.env.user.has_group('base.group_no_one')
        for ticket in self:
            if self.env.user.partner_id.id == ticket.partner_id.id or \
                    has_group:
                ticket.is_accessible = True
            if self.env.user.id == ticket.assigned_to_id.id or has_group:
                ticket.is_assigned = True

    @api.multi
    def _compute_attachments(self):
        for ticket in self:
            attachment_ids = self.env['ir.attachment'].search(
                    [('res_model', '=', ticket._name),
                     ('res_id', '=', ticket.id)])
            ticket.attachments_count = len(attachment_ids.ids)
            ticket.attachment_ids = attachment_ids

    @api.multi
    def action_get_attachments(self):
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,form',
            'view_type': 'form',
            'domain': [('res_model', '=', self._name),
                       ('res_id', '=', self.id)],
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (
                self._name, self.id),
        }

    @api.multi
    def action_get_issue_type(self):
        form_id = self.env.ref('helpdesk_basic.view_issue_type_form')
        tree_id = self.env.ref('helpdesk_basic.view_issue_type_tree')
        return {
            'name': 'Issue Types',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'issue.type',
            'views': [(tree_id.id, 'tree'), (form_id.id, 'form'), ],
            'domain': [('id', '=', self.issue_type_id.id)],
        }

    @api.multi
    def action_get_team(self):
        form_id = self.env.ref('helpdesk_basic.helpdesk_team_form_view')
        tree_id = self.env.ref('helpdesk_basic.helpdesk_team_tree_view')
        return {
            'name': 'Helpdesk Teams',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'helpdesk.team',
            'views': [(tree_id.id, 'tree'), (form_id.id, 'form'), ],
            'domain': [('id', '=', self.team_id.id)],
        }
