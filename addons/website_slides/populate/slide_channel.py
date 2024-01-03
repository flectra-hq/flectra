# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import models
from flectra.tools import populate


class SlideChannel(models.Model):
    _inherit = 'slide.channel'
    _populate_sizes = {'small': 2, 'medium': 8, 'large': 20}

    def _populate_factories(self):
        return [
            ('name', populate.constant('Course_{counter}')),
            ('description', populate.constant('This is course number {counter}')),
            ('website_published', populate.randomize([True, False], weights=[4, 1])),
        ]
