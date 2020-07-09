# -*- coding: utf-8 -*-

from flectra import api, fields, models, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    forma_pago = fields.Selection(selection=[('01', _('Efectivo')),
                                         ('02', _('Cheque')),
                                         ('03', _('Transferencia')),
                                         ('04', _('Tarjeta de crédito')),
                                         ('28', _('Tarjeta de débito')),
                                           ],
                                string=_('Forma de pago'), 
                            ) 