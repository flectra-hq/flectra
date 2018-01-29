# Part of Flectra See LICENSE file for full copyright and licensing details.

from datetime import datetime

from flectra.exceptions import Warning, AccessError, ValidationError
from flectra.tools.misc import formatLang

import flectra.addons.decimal_precision as dp
from flectra import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_indent_ids = fields.Many2many(
        'purchase.indent', string='Purchase Indent')

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id
        company = requisition.company_id
        currency = \
            partner.property_purchase_currency_id or \
            company.currency_id
        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.get_fiscal_position(partner.id)
        fpos = FiscalPosition.browse(fpos)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id,
        self.company_id = company.id
        self.currency_id = currency.id
        self.origin = requisition.name
        self.partner_ref = requisition.name
        self.notes = requisition.description
        self.date_order = requisition.date_end or fields.Datetime.now()
        self.picking_type_id = requisition.picking_type_id.id
        if requisition.type_id.line_copy != 'copy':
            return

        order_lines = []
        for line in requisition.line_ids:
            product_lang = line.product_id.with_context({
                'lang': partner.lang,
                'partner_id': partner.id,
            })
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            if fpos:
                taxes_ids = fpos.map_tax(
                    line.product_id.supplier_taxes_id.filtered(
                        lambda tax: tax.company_id == company))
            else:
                taxes_ids = line.product_id.supplier_taxes_id.filtered(
                    lambda tax: tax.company_id == company).ids

            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(
                    line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(
                    line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            if requisition.type_id.quantity_copy != 'copy':
                product_qty = 0

            if company.currency_id != currency:
                price_unit = requisition.company_id.currency_id.compute(
                    price_unit, currency)

            order_lines.append((0, 0, {
                'name': name,
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_po_id.id,
                'product_qty': product_qty,
                'price_unit': price_unit,
                'taxes_id': [(6, 0, taxes_ids)],
                'date_planned':
                    requisition.schedule_date or fields.Date.today(),
                'account_analytic_id': line.account_analytic_id.id,
                'purchase_indent_ids': [(6, 0, line.purchase_indent_ids.ids)],
                'purchase_indent_line_id': line.purchase_indent_line_id.id,
            }))
        self.order_line = order_lines

    @api.multi
    def button_draft(self):
        self.env['purchase.indent'].set_qty_state_confirm(self, False)
        return super(PurchaseOrder, self).button_draft()

    @api.multi
    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        for purchase_order_id in self:
            self.env['purchase.indent'].set_qty_state_cancel(
                purchase_order_id, False)
        return res

    @api.model
    def create(self, vals):
        if vals.get('requisition_id', False):
            requisition_id = self.requisition_id.browse(
                vals.get('requisition_id', False))
            if requisition_id.purchase_indent_ids:
                vals['purchase_indent_ids'] = \
                    [(6, 0, requisition_id.purchase_indent_ids.ids)]
        return super(PurchaseOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if vals.get('requisition_id', False):
            self.write({
                'purchase_indent_ids':
                    [(6, 0, self.requisition_id.purchase_indent_ids.ids)]})
        return res

    @api.multi
    def unlink(self):
        for record in self:
            if record.purchase_indent_ids:
                raise Warning(_("You can not delete Purchase order which \
                have reference of Purchase Indent!"))
        return super(PurchaseOrder, self).unlink()

    @api.multi
    def copy(self):
        self.ensure_one()
        if self.purchase_indent_ids:
            raise Warning(_("You can not copy Purchase order which have \
            reference of Purchase Indent!"))
        return super(PurchaseOrder, self).copy()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_indent_line_id = fields.Many2one(
        'purchase.indent.line', 'Purchase Indent Line Ref')
    purchase_indent_ids = fields.Many2many(
        'purchase.indent', string='Purchase Indent')

    @api.multi
    def unlink(self):
        if self.purchase_indent_line_id:
            raise Warning(_("You can not delete line which have \
            reference of Purchase Indent"))
        return super(PurchaseOrderLine, self).unlink()


class PurchaseRequisition(models.Model):
    _name = 'purchase.requisition'
    _inherit = ['purchase.requisition']

    purchase_indent_ids = fields.Many2many(
        'purchase.indent', string='Purchase Indent')
    branch_id = fields.Many2one('res.branch', string="Branch")

    @api.multi
    def action_draft(self):
        self.env['purchase.indent'].set_qty_state_confirm(False, self)
        return super(PurchaseRequisition, self).action_draft()

    @api.multi
    def action_cancel(self):
        self.env['purchase.indent'].set_qty_state_cancel(False, self)
        return super(PurchaseRequisition, self).action_cancel()

    @api.multi
    def unlink(self):
        for record in self:
            if record.purchase_indent_ids:
                raise Warning(_("You can not delete agreement which have \
                reference of Purchase Indent!"))
        return super(PurchaseRequisition, self).unlink()

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if self.purchase_indent_ids:
            raise Warning(_("You can not copy Purchase Agreement which \
            have reference of Purchase Indent!"))
        default.update(
            name=_("%s (copy)") % (self.name or ''))
        return super(PurchaseRequisition, self).copy(default)


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    purchase_indent_line_id = fields.Many2one(
        'purchase.indent.line', 'Purchase Indent Line Ref')
    purchase_indent_ids = fields.Many2many(
        'purchase.indent', string='Purchase Indent')
    branch_id = fields.Many2one(related='requisition_id.branch_id',
                                string='Branch', store=True)


class PurchaseIndent(models.Model):
    _name = 'purchase.indent'
    _inherit = ['mail.thread', 'mail.activity.mixin',
                'ir.branch.company.mixin']
    _description = "Purchase Indent"

    @api.multi
    def _compute_order_count(self):
        po_list = []
        pa_list = []
        for history_id in self.indent_history_ids:
            if history_id.order_id:
                po_list.append(history_id.order_id.id)
            elif history_id.purchase_requisition_id:
                pa_list.append(history_id.purchase_requisition_id.id)
        self.purchase_order_count = len(list(set(po_list)))
        self.agreement_count = len(list(set(pa_list)))

    @api.model
    def _default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = \
            self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'incoming'),
                                 ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'incoming'),
                                     ('warehouse_id', '=', False)])
        return types[:1]

    name = fields.Char(
        'Reference', index=True, copy=False,
        readonly=True, track_visibility='onchange')
    request_date = fields.Date(
        'Request Date', default=fields.Date.today(),
        track_visibility='onchange')
    category_id = fields.Many2one(
        'product.category', 'Category', track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'), ('confirm', 'Confirm'),
        ('requisition', 'Requisition'), ('done', 'Done'),
        ('cancel', 'Cancel')], 'State',
        default='draft', track_visibility='onchange')
    indent_line = fields.One2many(
        'purchase.indent.line', 'purchase_indent_id', 'Indent Lines')
    company_id = fields.Many2one(
        'res.company', string='Company', track_visibility='onchange')
    user_id = fields.Many2one(
        'res.users', string='Requested By',
        default=lambda self: self.env.uid,
        readonly=True, track_visibility='onchange')
    partner_id = fields.Many2one(
        'res.partner', related='user_id.partner_id',
        string="Partner", track_visibility='onchange')
    indent_history_ids = fields.One2many(
        'purchase.indent.history', 'purchase_indent_id', 'History')
    purchase_order_count = fields.Integer(
        compute='_compute_order_count', string='# of Purchase Order')
    agreement_count = fields.Integer(
        compute='_compute_order_count', string='# of Purchase Agreement')
    dest_address_id = fields.Many2one(
        'res.partner', string='Drop Ship Address',
        help="Put an address if you want to deliver directly from the vendor \
        to the customer.Otherwise, keep empty to deliver to your own company.")
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Deliver To', required=True,
        default=_default_picking_type,
        help="This will determine operation type of incoming shipment")
    default_location_dest_id_usage = fields.Selection(
        related='picking_type_id.default_location_dest_id.usage',
        string='Destination Location Type',
        help="Technical field used to display the Drop Ship Address",
        readonly=True)

    @api.constrains('company_id', 'branch_id')
    def _check_company(self):
        for order in self:
            if order.branch_id \
                    and order.company_id != order.branch_id.company_id:
                raise ValidationError(
                    _('Configuration Error of Company:\n'
                      'The Purchase Indent Company (%s) and '
                      'the Company (%s) of Branch must '
                      'be the same company!') % (
                        order.company_id.name,
                        order.branch_id.company_id.name)
                )

    @api.multi
    def set_qty_state_cancel(self, purchase_order_id=False,
                             purchase_agreement_id=False):
        indent_history_ids = []
        indent_line_obj = self.env['purchase.indent.line']
        if purchase_order_id:
            indent_history_ids = self.env['purchase.indent.history'].search([
                ('order_id', '=', purchase_order_id.id),
                ('purchase_requisition_id', '=', False)])
        elif purchase_agreement_id:
            indent_history_ids = self.env['purchase.indent.history'].search([
                ('order_id', '=', False),
                ('purchase_requisition_id', '=', purchase_agreement_id.id)])
        for history_id in indent_history_ids:
            indent_line_id = indent_line_obj.sudo().search([
                ('product_id', '=', history_id.product_id.id),
                ('purchase_indent_id', '=', history_id.purchase_indent_id.id)])
            requisition_qty = \
                indent_line_id.requisition_qty - history_id.requisition_qty
            indent_line_id.write({'requisition_qty': requisition_qty})
            history_id.purchase_indent_id.check_state()
            history_id.date = datetime.now()

    @api.multi
    def set_qty_state_confirm(self, purchase_order_id=False,
                              purchase_agreement_id=False):
        indent_line_obj = self.env['purchase.indent.line']
        indent_history_ids = []
        if purchase_order_id:
            indent_history_ids = self.env['purchase.indent.history'].search([
                ('order_id', '=', purchase_order_id.id),
                ('state', '=', 'Cancelled')])
        elif purchase_agreement_id:
            indent_history_ids = self.env['purchase.indent.history'].search([
                ('purchase_requisition_id', '=', purchase_agreement_id.id),
                ('state', '=', 'Cancelled')])
        for history_id in indent_history_ids:
            indent_line_id = indent_line_obj.sudo().search([
                ('product_id', '=', history_id.product_id.id),
                ('purchase_indent_id', '=', history_id.purchase_indent_id.id)])
            if indent_line_id.requisition_qty + history_id.requisition_qty > \
                    indent_line_id.product_qty:
                remaining_qty = \
                    indent_line_id.product_qty - indent_line_id.requisition_qty
                raise Warning(_("Requisition Quantity of ' %s ' is more than \
                Remaining Quantity (%s)!") % (
                    history_id.product_id.name, formatLang(
                        self.env, remaining_qty, digits=2)))
            requisition_qty = \
                indent_line_id.requisition_qty + history_id.requisition_qty
            indent_line_id.write({'requisition_qty': requisition_qty})
            history_id.purchase_indent_id.check_state()
            history_id.date = datetime.now()

    @api.onchange('company_id')
    def onchange_company_id(self):
        res = {}
        user_company_id = self.user_id.company_ids
        res['domain'] = {'company_id': [
            ('id', 'in', user_company_id.ids)]}
        if len(user_company_id) == 1:
            res['domain'] = {
                'company_id': [('id', '=', user_company_id.id)]}
            self.company_id = user_company_id.id
        return res

    @api.multi
    def check_duplicate_product(self):
        product_dup_list = []
        for line in self.indent_line:
            if line.product_id.id not in product_dup_list:
                product_dup_list.append(line.product_id.id)
            else:
                dup_line_id = self.env['purchase.indent.line'].search([
                    ('purchase_indent_id', '=', line.purchase_indent_id.id),
                    ('product_id', '=', line.product_id.id)], limit=1)
                dup_line_id.product_qty += line.product_qty
                line.unlink()

    @api.multi
    def action_confirm(self):
        if self._uid != self.create_uid.id:
            raise Warning(_("You can't confirm purchase indent which is \
            requested by %s!") % (self.create_uid.name))
        if not self.indent_line:
            raise Warning(_('No Product Line(s) were found!'))
        check_pro_qty = [
            line.id for line in self.indent_line if line.product_qty]
        if not check_pro_qty:
            raise Warning(_("No Quantity were found for any line!"))
        self.check_duplicate_product()
        group_id = self.sudo().env.ref('purchase.group_purchase_manager')
        if not group_id.users:
            raise AccessError(
                _("Please contact your Administrator \n \
                  No user found under 'Purchase Manager'"))
        server_id = self.env['ir.mail_server'].search([])
        if not server_id:
            raise AccessError(
                _("Please configure outgoing mail server"))
        email_to = ",".join([user.email
                             for user in group_id.users if user.email])
        recipient_ids = [user.partner_id.id for user in group_id.users]
        if self.env.user.email:
            product_qty = '''
                    <table width=100%% border="0" style="font-family: 'Arial';
                    font-size: 12px;">
                    <tr>
                        <td><b>''' + _("Product Name") + '''</b></td>
                        <td><b>''' + _("Quantity") + '''</b></td>
                        <td><b>''' + _("Expected Date") + '''</b></td>
                    </tr>'''
            for line in self.indent_line:
                qty = (str(formatLang(self.env, line.product_qty, digits=2)))
                product_qty += '<tr>\
                                    <td>' + str(line.product_id.name) + '</td>\
                                    <td>' + qty + '</td>\
                                    <td>' + str(line.expected_date) + '</td>\
                                </tr>'
            msg1 = '<p>Purchase Indent "%s" Confirmed by "%s" for following \
            Products Details.</p>' % (self.name, self.env.user.name)
            msg1 += '<p> %s </p>' % (product_qty)
            create_values = {
                'body_html': msg1,
                'subject': 'Purchase Indent Confirmed by %s' % (
                    self.env.user.name),
                'email_from': self.env.user.email,
                'email_to': email_to,
                'model': 'purchase.indent',
                'res_id': self.id,
                'reply_to': '',
                'recipient_ids': [(6, 0, recipient_ids)],
            }
            email_id = self.env['mail.mail'].create(create_values)
            email_id.send()
        else:
            raise AccessError(_("Please configure your email"))
        self.state = 'confirm'

    @api.multi
    def action_cancel(self):
        group_id = self.sudo().env.ref('purchase.group_purchase_manager')
        if self._uid != self.create_uid.id \
                and self._uid not in group_id.users.ids:
            raise Warning(_("Can't cancel purchase indent which is \
            requested by %s!") % (self.create_uid.name))
        self.state = 'cancel'

    @api.multi
    def button_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = \
                self.env['ir.sequence'].next_by_code('purchase.indent') or '/'
        return super(PurchaseIndent, self).create(vals)

    @api.multi
    def get_purchase_order_list(self):
        order_list = [
            history_id.order_id.id for history_id in self.indent_history_ids]
        return {
            'name': 'Purchase Orders',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form,kanban,pivot,graph',
            'res_model': 'purchase.order',
            'domain': [('id', 'in', list(set(order_list)))],
        }

    @api.multi
    def get_purchase_agreement_list(self):
        pr_list = [history_id.purchase_requisition_id.id
                   for history_id in self.indent_history_ids]
        return {
            'name': 'Purchase Agreements',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.requisition',
            'domain': [('id', 'in', list(set(pr_list)))],
        }

    @api.multi
    def unlink(self):
        for indent_id in self:
            if indent_id.state not in ['draft', 'cancel']:
                raise Warning(_("Invalid Action!\n You cannot delete a \
                Purchase Indent which is not in 'Draft' or 'Cancel' State!"))
            indent_id.indent_line.unlink()
        return super(PurchaseIndent, self).unlink()

    @api.multi
    def check_state(self):
        check = False
        state = ''
        for line in self.indent_line:
            if line.requisition_qty \
                    and line.product_qty != line.requisition_qty:
                state = 'requisition'
                check = False
                break
            elif not line.requisition_qty:
                if check:
                    state = 'requisition'
                    check = False
                    break
                state = 'confirm'
                check = False
            else:
                if line.product_qty != line.requisition_qty:
                    check = False
                    break
                else:
                    check = True
        if check:
            state = 'done'
        self.write({'state': state})


class PurchaseIndentLine(models.Model):
    _name = 'purchase.indent.line'
    _description = "Purchase Indent Line"

    @api.multi
    @api.depends('requisition_qty', 'product_qty')
    def _compute_get_rem_qty(self):
        for self_id in self:
            self_id.remaining_qty = \
                self_id.product_qty - self_id.requisition_qty

    purchase_indent_id = fields.Many2one('purchase.indent', 'Purchase Indent')
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(
        string='Request Quantity', digits=dp.get_precision('Discount'))
    expected_date = fields.Date(
        string='Expected Date', index=True, default=fields.Date.today())
    product_uom = fields.Many2one(
        'product.uom', string='Product Unit of Measure')
    product_id = fields.Many2one(
        'product.product', string='Product',
        change_default=True, required=True)
    company_id = fields.Many2one(
        'res.company', related='purchase_indent_id.company_id',
        string='Company', store=True, readonly=True)
    branch_id = fields.Many2one(related='purchase_indent_id.branch_id',
                                string='Branch', store=True)
    requisition_qty = fields.Float(
        string="Requisition Quantity",
        digits=dp.get_precision('Discount'))
    partner_id = fields.Many2one(
        'res.partner', related='purchase_indent_id.partner_id',
        string='Partner', readonly=True, store=True)
    remaining_qty = fields.Float(
        compute="_compute_get_rem_qty", string='Remaining Quantity',
        digits=dp.get_precision('Discount'), store=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [
            ('category_id', '=', self.product_id.uom_id.category_id.id)]}
        product_lang = self.product_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase
        return result

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        warning = {}
        if self.product_qty < 0:
            warning.update({
                'title': _("Warning"),
                'message': _("Quantity (%s) can not be Negative!") % (
                    formatLang(self.env, self.product_qty, digits=2))
            })
            self.product_qty = False
            return {'warning': warning}


class PurchaseIndentHistory(models.Model):
    _name = 'purchase.indent.history'
    _description = "Purchase Indent History"
    _order = 'id desc'

    @api.multi
    @api.depends('order_id.state', 'purchase_requisition_id.state')
    def _compute_get_state(self):
        for history_id in self:
            name = ""
            if history_id.order_id:
                po_dict = dict(history_id.order_id.fields_get(
                    allfields=['state'])['state']['selection'])
                name = po_dict.get(history_id.order_id.state)
            elif history_id.purchase_requisition_id:
                pa_dict = dict(history_id.purchase_requisition_id.fields_get(
                    allfields=['state'])['state']['selection'])
                name = pa_dict.get(history_id.purchase_requisition_id.state)
            history_id.state = name

    @api.multi
    @api.depends('requisition_qty', 'product_qty', 'state')
    def _compute_get_rem_qty(self):
        for self_id in self:
            if self_id.state == 'Cancelled':
                self_id.remaining_qty = self_id.product_qty
            else:
                self_id.remaining_qty = \
                    self_id.product_qty - self_id.requisition_qty

    purchase_indent_id = fields.Many2one('purchase.indent', 'Purchase Indent')
    branch_id = fields.Many2one(related='purchase_indent_id.branch_id',
                                string='Branch', store=True)
    company_id = fields.Many2one(related='purchase_indent_id.company_id',
                                 string="Company", store=True)
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain=[('purchase_ok', '=', True)],
        change_default=True, required=True)
    order_id = fields.Many2one('purchase.order', 'Purchase Order')
    purchase_requisition_id = fields.Many2one(
        'purchase.requisition', 'Purchase Agreement')
    date = fields.Datetime('Date')
    product_qty = fields.Float(
        'Quantity', digits=dp.get_precision('Discount'))
    requisition_qty = fields.Float(
        string="Transfer Quantity",
        digits=dp.get_precision('Discount'))
    state = fields.Char(compute='_compute_get_state', string='State',
                        store=True)
    remaining_qty = fields.Float(
        compute="_compute_get_rem_qty", string='Remaining Quantity',
        digits=dp.get_precision('Discount'), store=True)

    @api.multi
    def open_form_view(self):
        res_id = model = False
        if self.order_id:
            res_id = self.order_id.id
            model = 'purchase.order'
        elif self.purchase_requisition_id:
            res_id = self.purchase_requisition_id.id
            model = 'purchase.requisition'
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': model,
            'res_id': res_id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
