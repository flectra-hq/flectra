# Part of Flectra See LICENSE file for full copyright and licensing details.

from datetime import datetime

from flectra.exceptions import Warning
from flectra.tools.misc import formatLang

import flectra.addons.decimal_precision as dp
from flectra import api, fields, models, _


class WizRequisitionRequest(models.TransientModel):
    _name = 'wiz.requisition.request'

    purchase_indent_id = fields.Many2one('purchase.indent', 'Purchase Indent')
    branch_id = fields.Many2one('res.branch', string='Branch')
    partner_id = fields.Many2one(
        'res.partner', 'Vendor', domain="[('supplier','=',True)]")
    wiz_indent_line = fields.One2many(
        'wiz.indent.line', 'wizard_indent_id', string='Indent Lines')
    category_id = fields.Many2one(
        'product.category', 'Category', readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm')], default='draft')
    dummy_wiz_indent_line = fields.One2many(
        'dummy.wiz.indent.line', 'wizard_indent_id', string='Indent Lines')
    order_type = fields.Selection([
        ('po', 'Purchase Order'),
        ('pa', 'Purchase Agreement')], string='Order Type', default='po')
    requisition_type_id = fields.Many2one(
        'purchase.requisition.type', string="Agreement Type")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        obj_pro_sup = self.env['product.supplierinfo']
        for line in self.wiz_indent_line:
            pro_supplier_info_ids = obj_pro_sup.search([
                ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                ('name', '=', self.partner_id.id)])
            if pro_supplier_info_ids:
                line.price_unit = \
                    max([pro_sup_id.price
                         for pro_sup_id in pro_supplier_info_ids])

    @api.onchange('purchase_indent_id')
    def onchange_purchase_indent_id(self):
        if self.state == 'draft':
            purchase_indent_ids = self.purchase_indent_id.search([
                ('category_id', '=', self.purchase_indent_id.category_id.id),
                ('state', 'in', ['confirm', 'requisition']),
                ('branch_id', '=', self.purchase_indent_id.branch_id.id),
                ('company_id', '=', self.purchase_indent_id.company_id.id)])
            list_data = []
            value = {}
            for purchase_indent_id in purchase_indent_ids:
                for indent_line_id in purchase_indent_id.indent_line:
                    if not indent_line_id.product_qty == \
                            indent_line_id.requisition_qty:
                        list_data.append(
                            (0, 0, {
                                'partner_id': purchase_indent_id.partner_id.id,
                                'name': indent_line_id.name,
                                'product_id': indent_line_id.product_id.id,
                                'product_qty': indent_line_id.product_qty,
                                'dummy_product_qty':
                                    indent_line_id.product_qty,
                                'indent_requ_date':
                                    purchase_indent_id.request_date,
                                'expected_date': indent_line_id.expected_date,
                                'product_uom': indent_line_id.product_uom.id,
                                'purchase_indent_id': purchase_indent_id.id,
                                'purchase_indent_line_id': indent_line_id.id,
                                'wizard_indent_id': self.id
                            }))
            value['dummy_wiz_indent_line'] = list_data
            self.update(value)

    @api.onchange('order_type')
    def onchange_order_type(self):
        if self.order_type == 'po':
            self.requisition_type_id = False

    @api.multi
    def act_next(self):
        wiz_line_object = self.env['wiz.indent.line']
        dummy_wiz_line_object = self.env['dummy.wiz.indent.line']
        dup_product_list = []
        list_data = []
        unique_list = []
        check_requisition_qty = False

        for line in self.dummy_wiz_indent_line:
            if line.requisition_qty:
                check_requisition_qty = True
                line.requisition_qty = line.requisition_qty
                if line.product_id.id not in dup_product_list:
                    dup_product_list.append(line.product_id.id)
        if not check_requisition_qty:
            raise Warning(_("No Requisition Quantity were \
            found for any line!"))
        msg = 'Following Requisition Quantity is greater than Remaining ' \
              'Quantity!\n'
        check_warning = False
        for line in self.dummy_wiz_indent_line:
            if not line.requisition_qty:
                continue
            if line.requisition_qty > line.remaining_qty:
                check_warning = True
                msg += ("\n %s : Product (%s) => Requisition Quantity (%s) "
                        "and Remaining Quantity (%s)!") % (
                    line.purchase_indent_id.name, line.product_id.name,
                    formatLang(self.env, line.requisition_qty, digits=2),
                    formatLang(self.env, line.remaining_qty, digits=2))
        if check_warning:
            raise Warning(_(msg))
        for line in self.dummy_wiz_indent_line:
            if not line.requisition_qty:
                continue
            line_vals = {
                'purchase_indent_ids':
                    [(4, line.purchase_indent_id.id)],
                'partner_id': line.partner_id.id,
                'name': line.name,
                'product_id': line.product_id.id,
                'product_qty': line.requisition_qty,
                'product_uom': line.product_uom.id,
                'purchase_indent_line_id':
                    line.purchase_indent_line_id.id,
                'wizard_indent_id': self.id,
                'expected_date': line.expected_date,
                'taxes_id': [(6, 0, line.product_id.supplier_taxes_id.ids)],
            }
            if dup_product_list:
                if line.product_id.id not in unique_list:
                    new_line_id = wiz_line_object.create(line_vals)
                    unique_list.append(line.product_id.id)
                    list_data.append(new_line_id.id)
                else:
                    wiz_ids = dummy_wiz_line_object.search([
                        ('wizard_indent_id', '=', line.wizard_indent_id.id),
                        ('product_id', '=', line.product_id.id)])
                    wiz_indent_line_id = wiz_line_object.search([
                        ('wizard_indent_id', '=', self.id),
                        ('product_id', '=', line.product_id.id)])
                    indent_list = []
                    qty = 0.0
                    for wiz_id in wiz_ids:
                        indent_list.append(wiz_id.purchase_indent_id.id)
                        qty += wiz_id.requisition_qty
                    wiz_indent_line_id.write({
                        'product_qty': qty,
                        'purchase_indent_ids':
                            [(6, 0, list(set(indent_list)))]})
            else:
                new_line_id = wiz_line_object.create(line_vals)
                list_data.append(new_line_id.id)
        self.write(
            {'state': 'confirm', 'wiz_indent_line': [(6, False, list_data)]})
        view_id = \
            self.env.ref('purchase_indent.view_requisition_request_wizard')
        context = dict(self._context)
        return {
            'views': [(view_id.id, 'form')],
            'view_id': view_id.id,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wiz.requisition.request',
            'target': 'new',
            'res_id': self.id,
            'context': context,
        }

    @api.multi
    def action_create(self):
        list_data = []
        purchase_order_id = purchase_requisition_id = False
        obj_history_purchase_indent = self.env['purchase.indent.history']

        if self.order_type == 'po':
            vals = {
                'partner_id': self.partner_id.id,
                'state': 'draft',
                'branch_id': self.branch_id.id,
                'company_id': self.purchase_indent_id.company_id.id,
            }
            purchase_order_id = self.env['purchase.order'].with_context(
                {'branch_id': self.branch_id.id}).create(vals)
        else:
            vals = {
                'name': self.sudo().env['ir.sequence'].next_by_code(
                    'purchase.order.requisition') or 'New',
                'type_id': self.requisition_type_id.id,
                'branch_id': self.branch_id.id,
                'state': 'draft',
                'company_id': self.purchase_indent_id.company_id.id,
            }
            purchase_requisition_id = self.env[
                'purchase.requisition'].create(vals)
        indent_list = []
        for current_line in self.sudo().wiz_indent_line:
            current_line.purchase_indent_ids.write({'state': 'requisition'})
            indent_list.extend(current_line.purchase_indent_ids.ids)
            line_vals = {
                'product_id': current_line.product_id.id,
                'product_qty': current_line.product_qty,
                'branch_id': self.branch_id.id,
                'purchase_indent_ids':
                    [(6, 0, current_line.purchase_indent_ids.ids)],
                'purchase_indent_line_id':
                    current_line.purchase_indent_line_id.id,
                }
            if self.order_type == 'po':
                line_vals.update({
                    'name': current_line.name,
                    'date_planned': current_line.expected_date,
                    'partner_id': self.partner_id.id,
                    'price_unit': current_line.price_unit,
                    'taxes_id': [(6, 0, current_line.taxes_id.ids)],
                    'product_uom': current_line.product_uom.id,
                    })
            else:
                line_vals.update({
                    'product_uom_id': current_line.product_uom.id,
                    })
            list_data.append((0, 0, line_vals))
            if len(current_line.purchase_indent_ids.ids) > 1:
                for data in self.sudo().dummy_wiz_indent_line:
                    if data.product_id.id == current_line.product_id.id:
                        product_qty = data.purchase_indent_line_id.product_qty
                        requisition_qty = \
                            data.purchase_indent_line_id.requisition_qty
                        before_qty = product_qty - requisition_qty
                        data.purchase_indent_line_id.requisition_qty +=\
                            data.requisition_qty
                        obj_history_purchase_indent.create({
                            'purchase_indent_id': data.purchase_indent_id.id,
                            'product_id': data.product_id.id,
                            'order_id':
                                purchase_order_id and purchase_order_id.id,
                            'purchase_requisition_id':
                                purchase_requisition_id and
                                purchase_requisition_id.id,
                            'date': datetime.now(),
                            'product_qty': before_qty,
                            'requisition_qty': data.requisition_qty
                            })
            else:
                product_qty = current_line.purchase_indent_line_id.product_qty
                requisition_qty = \
                    current_line.purchase_indent_line_id.requisition_qty
                before_qty = product_qty - requisition_qty
                current_line.purchase_indent_line_id.requisition_qty +=\
                    current_line.product_qty
                obj_history_purchase_indent.create({
                    'purchase_indent_id': current_line.purchase_indent_ids.id,
                    'product_id': current_line.product_id.id,
                    'order_id': purchase_order_id and purchase_order_id.id,
                    'purchase_requisition_id':
                        purchase_requisition_id and purchase_requisition_id.id,
                    'date': datetime.now(),
                    'product_qty': before_qty,
                    'requisition_qty': current_line.product_qty,
                })
        if purchase_order_id:
            purchase_order_id.write({
                'order_line': list_data,
                'purchase_indent_ids': [(6, 0, indent_list)]})
        elif purchase_requisition_id:
            purchase_requisition_id.write({
                'line_ids': list_data,
                'purchase_indent_ids': [(6, 0, indent_list)]})
        self.check_state()

    @api.multi
    def check_state(self):
        purchase_indent_ids = self.purchase_indent_id.search([
            ('category_id', '=', self.purchase_indent_id.category_id.id),
            ('state', 'in', ['confirm', 'requisition']),
            ('branch_id', '=', self.purchase_indent_id.branch_id.id),
            ('company_id', '=', self.purchase_indent_id.company_id.id)])
        for purchase_indent_id in purchase_indent_ids:
            check = False
            for line in purchase_indent_id.indent_line:
                if line.product_qty != line.requisition_qty:
                    check = False
                    break
                else:
                    check = True
            if check:
                purchase_indent_id.write({'state': 'done'})


class WizIndentLine(models.TransientModel):
    _name = 'wiz.indent.line'
    _description = "Wizard Indent Line"

    @api.depends('purchase_indent_line_id',
                 'purchase_indent_line_id.product_qty',
                 'purchase_indent_line_id.requisition_qty')
    @api.multi
    def _compute_get_rem_qty(self):
        for line_id in self:
            remaining_qty = 0.0
            if line_id.purchase_indent_line_id:
                remaining_qty = \
                    line_id.purchase_indent_line_id.product_qty - \
                    line_id.purchase_indent_line_id.requisition_qty
            line_id.remaining_qty = remaining_qty

    purchase_indent_ids = fields.Many2many(
        'purchase.indent', string='Purchase Indent')
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(
        string='Quantity', digits=dp.get_precision('Discount'))
    expected_date = fields.Datetime(string='Expected Date', index=True)
    product_uom = fields.Many2one(
        'product.uom', string='Product Unit of Measure')
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain=[('purchase_ok', '=', True)],
        change_default=True, required=True)
    requisition_qty = fields.Float(
        string="Requisition Quantity",
        digits=dp.get_precision('Discount'))
    wizard_indent_id = fields.Many2one(
        'wiz.requisition.request', 'Wiz Requisition Request')

    partner_id = fields.Many2one('res.partner', string='Partner')
    price_unit = fields.Float(
        string='Unit Price', digits=dp.get_precision('Product Price'))
    taxes_id = fields.Many2many(
        'account.tax', string='Taxes',
        domain=['|', ('active', '=', False), ('active', '=', True)])
    purchase_indent_line_id = fields.Many2one(
        'purchase.indent.line', string="Indent Line Ref")
    remaining_qty = fields.Float(
        compute='_compute_get_rem_qty', string='Remaining Quantity',
        store=True)
    order_type = fields.Selection(
        related='wizard_indent_id.order_type', string='Order Type')


class DummyWizIndentLine(models.TransientModel):
    _name = 'dummy.wiz.indent.line'
    _description = "Dummy Wizard Indent Line"

    @api.depends('purchase_indent_line_id',
                 'purchase_indent_line_id.product_qty',
                 'purchase_indent_line_id.requisition_qty')
    @api.multi
    def _compute_get_rem_qty(self):
        for line_id in self:
            remaining_qty = 0.0
            if line_id.purchase_indent_line_id:
                remaining_qty = \
                    line_id.purchase_indent_line_id.product_qty - \
                    line_id.purchase_indent_line_id.requisition_qty
            line_id.remaining_qty = remaining_qty

    purchase_indent_id = fields.Many2one(
        'purchase.indent', 'Purchase Indent',
        domain="[('id', '=', purchase_indent_id)]")
    name = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(
        string='Quantity', digits=dp.get_precision('Discount'))
    dummy_product_qty = fields.Float(string='Quantity',
                                     digits=dp.get_precision('Discount'))
    expected_date = fields.Datetime(string='Expected Date', index=True)
    product_uom = fields.Many2one(
        'product.uom', string='Product Unit of Measure')
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('purchase_ok', '=', True), ('id', '=', product_id)]",
        change_default=True, required=True)
    company_id = fields.Many2one(
        'res.company', related='purchase_indent_id.company_id',
        string='Company', store=True, readonly=True)
    requisition_qty = fields.Float(
        string="Requisition Quantity",
        digits=dp.get_precision('Product Unit of Measure'))
    wizard_indent_id = fields.Many2one(
        'wiz.requisition.request', 'Wiz Requisition Request')
    partner_id = fields.Many2one(
        'res.partner', related='purchase_indent_id.partner_id',
        string='Partner', readonly=True, store=True)
    indent_requ_date = fields.Date(
        related='purchase_indent_id.request_date',
        string='Request Date', readonly=True, store=True)
    purchase_indent_line_id = fields.Many2one(
        'purchase.indent.line', string="Indent Line Ref")
    remaining_qty = fields.Float(
        compute='_compute_get_rem_qty', string='Remaining Quantity',
        store=True)

    @api.onchange('requisition_qty')
    def onchange_requisition_qty(self):
        warning = {}
        if self.requisition_qty < 0:
            warning.update({
                'title': _("Warning"),
                'message': _("Requisition Quantity (%s) can not be \
                Negative!") % (
                    formatLang(self.env, self.requisition_qty, digits=2))
            })
            self.requisition_qty = False
            return {'warning': warning}

    @api.model
    def create(self, values):
        if values.get('dummy_product_qty', False):
            values.update({'product_qty': values.get('dummy_product_qty')})
        res = super(DummyWizIndentLine, self).create(values)
        return res

    @api.model
    def write(self, values):
        if values.get('dummy_product_qty', False):
            values.update({'product_qty': values.get('dummy_product_qty')})
        res = super(DummyWizIndentLine, self).write(values)
        return res
