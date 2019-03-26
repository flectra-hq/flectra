# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import json
import base64

from flectra import models,api
from flectra.http import request
from .crypt import *

import flectra


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def webclient_rendering_context(self):
        return {
            'menu_data': request.env['ir.ui.menu'].load_menus(request.debug),
            'session_info': json.dumps(self.session_info()),
        }

    def session_info(self):
        user = request.env.user
        display_switch_company_menu = user.has_group('base.group_multi_company') and len(user.company_ids) > 1
        version_info = flectra.service.common.exp_version()
        ir_module_module_ids = self.env['ir.module.module'].sudo().search(
            [('contract_certificate', '!=', False), ('state', '=', 'installed')])
        IrConfig = request.env['ir.config_parameter'].sudo()
        contracted_module_list, is_valid = None, False
        if ir_module_module_ids:
            contracted_module_list = str(self.get_contracted_modules(ir_module_module_ids=ir_module_module_ids))
            is_valid = self.check_validate_date(IrConfig)
        else:
            is_valid = True

        return {
            "session_id": request.session.sid,
            "uid": request.session.uid,
            "is_system": request.env.user._is_system() if request.session.uid else False,
            "is_superuser": request.env.user._is_superuser() if request.session.uid else False,
            "user_context": request.session.get_context() if request.session.uid else {},
            "db": request.session.db,
            "server_version": version_info.get('server_version'),
            "server_version_info": version_info.get('server_version_info'),
            "name": user.name,
            "username": user.login,
            "company_id": request.env.user.company_id.id if request.session.uid else None,
            "partner_id": request.env.user.partner_id.id if request.session.uid and request.env.user.partner_id else None,
            "user_companies": {'current_company': (user.company_id.id, user.company_id.name), 'allowed_companies': [(comp.id, comp.name) for comp in user.company_ids]} if display_switch_company_menu else False,
            "currencies": self.get_currencies() if request.session.uid else {},
            "web.base.url": self.env['ir.config_parameter'].sudo().get_param('web.base.url', default=''),
            'expiration_date' : IrConfig.get_param('database.expiration_date'),
            'expiration_reason': IrConfig.get_param('database.expiration_reason'),
            'contracted_module_list': contracted_module_list,
            'contract_validation':is_valid
        }

    def get_currencies(self):
        Currency = request.env['res.currency']
        currencies = Currency.search([]).read(['symbol', 'position', 'decimal_places'])
        return { c['id']: {'symbol': c['symbol'], 'position': c['position'], 'digits': [69,c['decimal_places']]} for c in currencies} 

    def get_contracted_modules(self, type=None, contract_key=None, ir_module_module_ids=None):
        if ir_module_module_ids:
            contract_key = contract_key or ''
            contracted_module_list = ir_module_module_ids.mapped('name')
            warrant = self.env['publisher_warranty.contract'].sudo()._get_message()
            warrant.update({
                'contracts': contracted_module_list,
                'contract_id': contract_key
            })
            if type != 'online':
                contracts = encrypt(json.dumps(warrant), contract_key)
            else:
                contracts = str.encode(json.dumps(warrant))
            return contracts

    @api.model
    def contract_validate_file(self, contract_id, type):
        contracts = []
        if contract_id:
            ir_module_module_ids = self.env['ir.module.module'].sudo().search(
                [('contract_certificate', '!=', False), ('state', '=', 'installed')])
            contracts = self.get_contracted_modules(type, contract_id, ir_module_module_ids)
        return json.dumps(base64.encodestring(contracts).decode('ascii'))

    def check_validate_date(self, config):
        exp_date = config.get_param('database.expiration_date')
        validity = config.get_param('contract.validity')
        try:
            decrypt(base64.decodestring(str.encode(validity)), str(exp_date))
        except Exception:
            return False
        return True
