# -*- coding: utf-8 -*-
# Copyright 2016, 2019 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from flectra import models, fields


class ResUsers(models.Model):

    _inherit = 'res.users'

    chatter_position = fields.Selection(
        [("bottom", "Bottom"), ("sided", "Sided")],
        string="Chatter Position",
        default="sided",
    )
    dark_mode = fields.Boolean(default=False)

    def init(self):
        """ Override of __init__ to add access rights on notification_email_send
            and alias fields. Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        # super(ResUsers, self).__init__(pool, cr)

        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(["chatter_position"])
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(["chatter_position"])
