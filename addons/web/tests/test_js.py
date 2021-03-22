# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

import re
import flectra.tests

RE_ONLY = re.compile('QUnit\.only\(')


@flectra.tests.tagged('post_install', '-at_install')
class WebSuite(flectra.tests.HttpCase):

    def test_js(self):
        # webclient desktop test suite
        self.browser_js('/web/tests?mod=web&failfast', "", "", login='admin', timeout=1800)

    def test_check_suite(self):
        # verify no js test is using `QUnit.only` as it forbid any other test to be executed
        self._check_only_call('web.qunit_suite_tests')
        self._check_only_call('web.qunit_mobile_suite_tests')

    def _check_only_call(self, suite):
        # As we currently aren't in a request context, we can't render `web.layout`.
        # redefinied it as a minimal proxy template.
        self.env.ref('web.layout').write({'arch_db': '<t t-name="web.layout"><head><meta charset="utf-8"/><t t-raw="head"/></head></t>'})

        for asset in self.env['ir.qweb']._get_asset_content(suite, options={})[0]:
            filename = asset['filename']
            if not filename or asset['atype'] != 'text/javascript':
                continue
            with open(filename, 'rb') as fp:
                if RE_ONLY.search(fp.read().decode('utf-8')):
                    self.fail("`QUnit.only()` used in file %r" % asset['url'])


@flectra.tests.tagged('post_install', '-at_install')
class MobileWebSuite(flectra.tests.HttpCase):
    browser_size = '375x667'

    def test_mobile_js(self):
        # webclient mobile test suite
        self.browser_js('/web/tests/mobile?mod=web&failfast', "", "", login='admin', timeout=1800)
