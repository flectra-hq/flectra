# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import logging
import flectra.tests

_logger = logging.getLogger(__name__)


@flectra.tests.tagged('click_all', 'post_install', '-at_install', '-standard')
class TestMenusAdmin(flectra.tests.HttpCase):

    def test_01_click_everywhere_as_admin(self):
        menus = self.env['ir.ui.menu'].load_menus(False)
        for app in menus['children']:
                with self.subTest(app=app['name']):
                    _logger.runbot('Testing %s', app['name'])
                    self.browser_js("/web", "flectra.__DEBUG__.services['web.clickEverywhere']('%s');" % app['xmlid'], "flectra.isReady === true", login="admin", timeout=300)
                    self.terminate_browser()


@flectra.tests.tagged('click_all', 'post_install', '-at_install', '-standard')
class TestMenusDemo(flectra.tests.HttpCase):

    def test_01_click_everywhere_as_demo(self):
        menus = self.env['ir.ui.menu'].load_menus(False)
        for app in menus['children']:
                with self.subTest(app=app['name']):
                    _logger.runbot('Testing %s', app['name'])
                    self.browser_js("/web", "flectra.__DEBUG__.services['web.clickEverywhere']('%s');" % app['xmlid'], "flectra.isReady === true", login="demo", timeout=300)
                    self.terminate_browser()

@flectra.tests.tagged('post_install', '-at_install')
class TestMenusAdminLight(flectra.tests.HttpCase):

    def test_01_click_apps_menus_as_admin(self):
        self.browser_js("/web", "flectra.__DEBUG__.services['web.clickEverywhere'](undefined, true);", "flectra.isReady === true", login="admin", timeout=120)

@flectra.tests.tagged('post_install', '-at_install',)
class TestMenusDemoLight(flectra.tests.HttpCase):

    def test_01_click_apps_menus_as_demo(self):
            self.browser_js("/web", "flectra.__DEBUG__.services['web.clickEverywhere'](undefined, true);", "flectra.isReady === true", login="demo", timeout=120)
