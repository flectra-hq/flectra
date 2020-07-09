# -*- coding: utf-8 -*-
from flectra import models,fields,api
from flectra.exceptions import Warning
import os
from lxml import etree
import base64

class import_account_payment_from_xml(models.TransientModel):
    _name ='import.account.payment.from.xml'
    
    import_file = fields.Binary("Importar Archivo",required=False)
    file_name = fields.Char("Nombre del archivo")
    payment_id = fields.Many2one("account.payment",'Payment')
    
    @api.multi
    def import_xml_file_button(self):
        self.ensure_one()
        if not self.import_file:
            raise Warning("Seleccione primero el archivo.")
        p, ext = os.path.splitext(self.file_name)
        if ext[1:].lower() !='xml':
            raise Warning(_("Formato no soportado \"{}\", importa solo archivos XML").format(self.file_name))
        
        file_content = base64.b64decode(self.import_file)
        tree = etree.fromstring(file_content)
        payment_vals = {
            'cep_sello': tree.get('sello'),
            'cep_numeroCertificado' : tree.get('numeroCertificado',tree.get('NumeroCertificado')),
            'cep_cadenaCDA' : tree.get('cadenaCDA',tree.get('CadenaCDA')),
            'cep_claveSPEI' : tree.get('ClaveSPEI',tree.get('claveSPEI')),
            }
        self.payment_id.write(payment_vals)
        return True
    
    
         