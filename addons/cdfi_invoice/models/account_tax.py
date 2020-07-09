# -*- coding: utf-8 -*-
from flectra import fields, models, api,_

    
class AccountTax(models.Model):
    _inherit = 'account.tax'
    
    
    impuesto = fields.Selection(selection=[('002', 'IVA'),
                                           ('003', ' IEPS'),
                                           ('001', 'ISR'),
                                           ('004', 'ISH')], string='Impuesto')
    tipo_factor = fields.Selection(selection=[('Tasa', 'Tasa'),
                                           ('Cuota', 'Cuota'),
                                           ('Exento', 'Exento')], string='Tipo factor')

            
     