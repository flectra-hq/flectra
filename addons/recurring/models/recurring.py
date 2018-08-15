# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing
# details.

# TODO:
#   Error treatment: exception, request, ... -> send request to user_id

from flectra import api, fields, models, _
from flectra.exceptions import UserError, ValidationError


def _get_document_types(self):
    return [(doc.model.model, doc.name) for doc in self.env[
        'recurring.document'].search([], order='name')]


class RecurringDocument(models.Model):
    _name = "recurring.document"
    _description = "Recurring Document"

    name = fields.Char(string='Name')
    active = fields.Boolean(
        help="If the active field is set to False, it will allow you to hide "
             "the recurring document without removing it.", default=True)
    model = fields.Many2one('ir.model', string="Object")
    field_ids = fields.One2many('recurring.document.fields',
                                'document_id', string='Fields', copy=True)


class RecurringDocumentFields(models.Model):
    _name = "recurring.document.fields"
    _description = "Recurring Document Fields"
    _rec_name = 'field'

    field = fields.Many2one('ir.model.fields', domain="[('model_id', '=', "
                                                      "parent.model)]")
    value = fields.Selection(
        [('false', 'False'), ('date', 'Current Date')], string='Default Value',
        help="Default value is considered for field when new document is "
             "generated.")
    document_id = fields.Many2one('recurring.document',
                                  string='Recurring Document',
                                  ondelete='cascade')


class Recurring(models.Model):
    _name = "recurring"
    _description = "Recurring"

    @api.model
    def default_get(self, fields):
        res = super(Recurring, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_model and active_id:
            record = self.env[active_model].browse(active_id)
            if 'partner_id' in self.env[active_model]._fields:
                res['partner_id'] = record.partner_id.id
            else:
                res['name'] = record.name
                if not res['name']:
                    res['name'] = record.number
        return res

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if self.partner_id and active_model and active_id:
            record = self.env[active_model].browse(active_id)
            name = record.name
            if not name:
                name = record.number
            if name:
                self.name = name + '-' + self.partner_id.name
            else:
                self.name = self.partner_id.name

    @api.constrains('partner_id', 'doc_source')
    def _check_partner_id_doc_source(self):
        for record in self:
            if record.partner_id and record.doc_source and 'partner_id' in \
                    self.env[record.doc_source._name]._fields and \
                    record.doc_source.partner_id != record.partner_id:
                raise ValidationError(_(
                    'Error! Source Document should be related to partner %s' %
                    record.doc_source.partner_id.name))

    name = fields.Char(string='Name')
    active = fields.Boolean(
        help="If the active field is set to False, it will allow you to hide "
             "the recurring without removing it.", default=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    notes = fields.Text(string='Internal Notes')
    user_id = fields.Many2one('res.users', string='User',
                              default=lambda self: self.env.user)
    interval_number = fields.Integer(string='Internal Qty', default=1)
    interval_type = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'),
         ('weeks', 'Weeks'), ('months', 'Months')], string='Interval Unit',
        default='months')
    exec_init = fields.Integer(string='Number of Documents')
    date_init = fields.Datetime(string='First Date',
                                default=fields.Datetime.now)
    state = fields.Selection(
        [('draft', 'Draft'), ('running', 'Running'), ('done', 'Done')],
        string='Status', copy=False, default='draft')
    doc_source = fields.Reference(
        selection=_get_document_types, string='Source Document',
        help="User can choose the source document on which he wants to "
             "create documents")
    doc_lines = fields.One2many('recurring.history',
                                'recurring_id', string='Documents created')
    cron_id = fields.Many2one('ir.cron', string='Cron Job',
                              help="Scheduler which runs on recurring",
                              states={'running': [('readonly', True)],
                                      'done': [('readonly', True)]})
    note = fields.Text(string='Notes',
                       help="Description or Summary of Recurring")

    @api.model
    def _auto_end(self):
        super(Recurring, self)._auto_end()
        # drop the FK from recurring to ir.cron, as it would cause deadlocks
        # during cron job execution. When model_copy() tries to write() on
        # the recurring,
        # it has to wait for an ExclusiveLock on the cron job record,
        # but the latter is locked by the cron system for the duration of
        # the job!
        # FIXME: the recurring module should be reviewed to simplify the
        # scheduling process
        # and to use a unique cron job for all recurrings, so that it
        # never needs to be updated during its execution.
        self.env.cr.execute("ALTER TABLE %s DROP CONSTRAINT %s" % (
            self._table, '%s_cron_id_fkey' % self._table))

    @api.multi
    def create_recurring_type(self):
        rec_doc_obj = self.env['recurring.document']
        ir_model_id = self.env['ir.model'].search(
            [('model', '=', self._context.get('active_model', False))])
        rec_doc_id = rec_doc_obj.search([('model', '=', ir_model_id.id)])
        if not rec_doc_id:
            rec_doc_id = rec_doc_obj.create({
                'name': ir_model_id.name,
                'model': ir_model_id.id,
            })
        return rec_doc_id

    @api.multi
    def btn_recurring(self):
        self.ensure_one()
        rec_doc_id = self.create_recurring_type()
        if rec_doc_id:
            active_model = self._context.get('active_model')
            active_id = self._context.get('active_id')
            if active_id and active_model:
                record = self.env[active_model].browse(active_id)
                self.doc_source = record._name + "," + str(record.id)
                record.recurring_id = self.id
                record.rec_source_id = record.id
            if self._context.get('process') == 'start':
                self.set_process()

    @api.multi
    def set_process(self):
        for recurring in self:
            model = 'recurring'
            cron_data = {
                'name': recurring.name,
                'interval_number': recurring.interval_number,
                'interval_type': recurring.interval_type,
                'numbercall': recurring.exec_init,
                'nextcall': recurring.date_init,
                'model_id': self.env['ir.model'].search(
                    [('model', '=', model)]).id,
                'priority': 6,
                'user_id': recurring.user_id.id,
                'state': 'code',
                'code': 'model._cron_model_copy('+repr([recurring.id])+')',
            }
            cron = self.env['ir.cron'].sudo().create(cron_data)
            recurring.write({'cron_id': cron.id, 'state': 'running'})

    @api.multi
    def set_recurring_id(self):
        if self.doc_source and 'recurring_id' and 'rec_source_id' in \
                self.env[self.doc_source._name]._fields:
            rec_id = self.env[self.doc_source._name].browse(self.doc_source.id)
            if not rec_id.recurring_id and not rec_id.rec_source_id:
                rec_id.recurring_id = self.id
                rec_id.rec_source_id = self.doc_source.id
            else:
                raise ValidationError(
                    _('Document is already recurring'))

    @api.model
    def create(self, vals):
        if vals.get('doc_source', False) and self.search(
                [('doc_source', '=', vals['doc_source'])]):
            raise ValidationError(
                _('Recurring of the selected Source Document already exist'))
        res = super(Recurring, self).create(vals)
        res.set_recurring_id()
        return res

    @api.multi
    def write(self, values):
        doc_source_id = False
        if values.get('doc_source', False):
            doc_source_id = self.doc_source
        res = super(Recurring, self).write(values)
        if doc_source_id:
            rec_id = self.env[doc_source_id._name].browse(doc_source_id.id)
            rec_id.recurring_id = False
            self.set_recurring_id()
        return res

    @api.multi
    def get_recurring(self, model, active_id):
        result = self.env.ref('recurring.action_recurring_form').read()[0]
        record = self.env[model].browse(active_id)
        rec_ids = self.env['recurring'].search(
            [('doc_source', '=', record._name + "," + str(record.id))])
        result['domain'] = [('id', 'in', rec_ids.ids)]
        return result

    @api.multi
    def get_recurring_documents(self, model, action, recurring_id):
        result = self.env.ref(action).read()[0]
        res_ids = self.env[model].search(
            [('recurring_id', '=', recurring_id.id)])
        result['domain'] = [('id', 'in', res_ids.ids)]
        return result

    @api.model
    def _cron_model_copy(self, ids):
        self.browse(ids).model_copy()

    @api.multi
    def model_copy(self):
        for recurring in self.filtered(lambda sub: sub.cron_id):
            if not recurring.doc_source.exists():
                raise UserError(_('Please provide another source '
                                  'document.\nThis one does not exist!'))

            default = {}
            documents = self.env['recurring.document'].search(
                [('model.model', '=', recurring.doc_source._name)], limit=1)
            fieldnames = dict((f.field.name, f.value == 'date' and
                               fields.Date.today() or False)
                              for f in documents.field_ids)
            default.update(fieldnames)
            # if there was only one remaining document to generate
            # the recurring is over and we mark it as being done
            if recurring.cron_id.numbercall == 1:
                recurring.write({'state': 'done'})
            else:
                recurring.write({'state': 'running'})
            copied_doc = recurring.doc_source.copy(default)
            self.env['recurring.history'].create({
                'recurring_id': recurring.id,
                'date': fields.Datetime.now(),
                'document_id': '%s,%s' % (recurring.doc_source._name,
                                          copied_doc.id)})

    @api.multi
    def unlink(self):
        if any(self.filtered(lambda s: s.state == "running")):
            raise UserError(_('You cannot delete an active recurring!'))
        return super(Recurring, self).unlink()

    @api.multi
    def set_done(self):
        self.mapped('cron_id').write({'active': False})
        self.write({'state': 'done'})

    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})


class RecurringHistory(models.Model):
    _name = "recurring.history"
    _description = "Recurring history"
    _rec_name = 'date'

    date = fields.Datetime(string='Date')
    recurring_id = fields.Many2one('recurring', string='Recurring',
                                   ondelete='cascade')
    document_id = fields.Reference(
        selection=_get_document_types, string='Source Document')
