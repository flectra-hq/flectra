# -*- coding: utf-8 -*-

from flectra import api, fields, models


class Users(models.Model):
    _inherit = "res.users"

    bookmark_ids = fields.One2many('menu.bookmark', 'user_id', string="Bookmark Records")


class MenuBookmark(models.Model):
    _name = "menu.bookmark"

    menu_id = fields.Many2one('ir.ui.menu', 'Menu Id', help='Bookmark Menu Id', required=True)
    user_id = fields.Many2one('res.users', 'User Id', help='Bookmark User ID', required=True)

    @api.multi
    def bookmark(self, action_id):
        if action_id:
            menu = self.env['ir.ui.menu'].search([('action', 'like', '%,' + str(action_id))], limit=1)
            if not menu:
                action = self.env['ir.actions.actions'].browse(int(action_id))
                menu = self.env['ir.ui.menu'].search([('name', '=', action.name), ('action', '!=', '')], limit=1)
            rec = self.sudo().search(
                [('menu_id', '=', menu.id),
                 ('user_id', '=', self.env.user.id)])
            if (rec):
                if (rec.sudo().unlink()):
                    return {
                        'bookmark': False
                    }
            else:
                if (menu and menu.action):
                    if (self.sudo().create({
                        'menu_id': menu.id,
                        'user_id': self.env.user.id,
                    })):
                        return {
                            'bookmark': True
                        }
        return {}

    @api.multi
    def is_bookmark(self, menu_id):
        menu = self.env['ir.ui.menu'].browse(int(menu_id))
        if (menu and menu.action):
            rec = self.sudo().search(
                [('menu_id', '=', menu_id),
                 ('user_id', '=', self.env.user.id)])
            if (rec):
                return True
        return False

    @api.multi
    def get_bookmark_data(self, fields=[]):
        bookmark_menu_ids = [rec.menu_id.id for rec in self.sudo().search([('user_id', '=', self.env.user.id)])]
        menu_ids = self.env['ir.ui.menu'].browse(bookmark_menu_ids)
        data = menu_ids.read(fields)
        return sorted(data, key=lambda s: s['bookmark_label'])

    @api.multi
    def remove_bookmark(self, menu_id):
        if menu_id:
            rec = self.sudo().search(
                [('menu_id', '=', menu_id),
                 ('user_id', '=', self.env.user.id)])
            if rec:
                json = {
                    'id': rec.id,
                    'action_id': rec.menu_id.action.id,
                    'menu_id': rec.menu_id.id,
                }
                rec.sudo().unlink()
                return json
        return False
