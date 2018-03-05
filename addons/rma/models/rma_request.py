# Part of Flectra See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.exceptions import UserError


class RmaRequest(models.Model):
    _name = "rma.request"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "RMA Request"

    name = fields.Char(string='RMA Order Number')
    sale_order_id = fields.Many2one('sale.order', string='SO Number')
    picking_id = fields.Many2one('stock.picking', string='Picking Number')
    date = fields.Date(string='Request Date',
                       default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Customer')
    type = fields.Selection([
        ('return_replace', 'Return/Replace')
    ], string='Request Type')
    rma_line = fields.One2many('rma.line', 'rma_id', string='RMA Lines')
    warranty_expire_line = fields.One2many('warranty.expire.line', 'rma_id',
                                           string='Warranty Expire Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('rma_created', 'RMA Created'),
        ('replacement_created', 'Replacement Created'),
    ], string='Request Status', track_visibility='onchange', readonly=True,
        copy=False, default='draft')
    picking_count = fields.Integer(string='Delivery',
                                   compute="_compute_picking")
    picking_ids = fields.Many2many('stock.picking',
                                   string='Delivery',
                                   compute="_compute_picking")
    user_id = fields.Many2one('res.users', string='User',
                              default=lambda self: self.env.user)
    team_id = fields.Many2one('crm.team', string='Team')
    is_website = fields.Boolean(string="Website")
    is_replacement = fields.Boolean(string="Replacement?")

    @api.multi
    def _compute_picking(self):
        for request in self:
            picking_ids = self.env['stock.picking'].search([(
                'rma_id', '=', request.id)])
            request.picking_ids = picking_ids and picking_ids.ids or False
            request.picking_count = len(picking_ids)

    @api.onchange('sale_order_id')
    def _get_partner(self):
        if self.sale_order_id:
            self.partner_id = self.sale_order_id.partner_id and \
                self.sale_order_id.partner_id.id or False
            self.team_id = self.sale_order_id.team_id and \
                self.sale_order_id.team_id.id or False

    @api.onchange('picking_id')
    def _get_rma_lines(self):
        if self.picking_id and not self.is_website:
            move_line_ids = self.env['stock.move'].search([(
                'picking_id', '=', self.picking_id.id)])
            move_lines = [(5, 0, 0)]
            for line in move_line_ids:
                move_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'uom_id': line.product_uom.id,
                    'qty_delivered': line.quantity_done,
                    'qty_return': sum(line.qty_done for line in
                                      line.move_line_ids if
                                      line.lot_id.warranty_date and
                                      line.lot_id.warranty_date >= self.date
                                      ),
                    'rma_id': self.id,
                    'move_line_id': line.id
                }))
            self.rma_line = move_lines

    @api.onchange('rma_line', 'date')
    def _get_warranty_lines(self):
        warranty_lines = [(5, 0, 0)]
        for line in self.rma_line:
            if line.move_line_id and \
                    line.move_line_id.product_id.tracking != 'none':
                for move_line in line.move_line_id.move_line_ids:
                    if move_line.lot_id.warranty_date and \
                                    move_line.lot_id.warranty_date < self.date:
                        warranty_lines.append((0, 0, {
                            'product_id': move_line.product_id.id,
                            'lot_id': move_line.lot_id.id,
                            'warranty_date':
                                move_line.lot_id.warranty_date,
                            'qty_expired': sum(line.qty_done for line in
                                               line.move_line_id.move_line_ids
                                               if line.lot_id.warranty_date and
                                               line.lot_id.
                                               warranty_date < self.date),
                            'rma_id': self.id,
                        }))
        self.warranty_expire_line = warranty_lines

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code(
                'rma_order')
        })
        return super(RmaRequest, self).create(vals)

    @api.multi
    def action_create_delivery(self):
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]
        if len(self.picking_ids) != 1:
            result.update({
                'domain': "[('id', 'in', " + str(self.picking_ids.ids) + ")]"
            })
        elif len(self.picking_ids) == 1:
            res = self.env.ref('rma.view_picking_form', False)
            result.update({
                'views': [(res and res.id or False, 'form')],
                'res_id': self.picking_ids.id
            })
        return result

    @api.multi
    def action_notify_warranty(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'rma', 'email_template_notify_warranty_date')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(
            default_model='rma.request',
            default_res_id=self.id,
            default_use_template=bool(template_id),
            default_template_id=template_id,
            default_composition_mode='comment',
            force_email=True
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'draft' and self.rma_line:
            return 'rma.mt_request_create'
        elif 'state' in init_values and self.state == 'confirmed' and \
                self.rma_line:
            return 'rma.mt_request_confirm'
        elif 'state' in init_values and self.state == 'rma_created':
            return 'rma.mt_request_return'
        return super(RmaRequest, self)._track_subtype(init_values)

    @api.multi
    def action_confirm_request(self):
        self.ensure_one()
        if not self.rma_line:
            raise UserError(_('You must select rma lines!'))
        if not self.is_website:
            for line in self.rma_line:
                line._onchange_qty_return()
        self.state = 'confirmed'

    @api.multi
    def unlink(self):
        for request in self:
            if request.state != 'draft':
                raise UserError(_(
                    'You cannot delete a request which is not in draft '
                    'state.'))
        return super(RmaRequest, self).unlink()
