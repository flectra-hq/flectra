# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra.addons.base.tests.common import HttpCaseWithUserDemo, HttpCaseWithUserPortal

from flectra import http
from flectra.tests.common import tagged


@tagged('post_install', '-at_install')
class TestAuthSignupFlowWith2faEnforced(HttpCaseWithUserPortal, HttpCaseWithUserDemo):

    def setUp(self):
        super().setUp()
        self.env['res.config.settings'].create(
            {
                # Activate free signup
                'auth_signup_uninvited': 'b2c',
                # Enforce 2FA for all users
                'auth_totp_enforce': True,
                'auth_totp_policy': 'all_required',
            }
        ).execute()

    def test_signup_with_2fa_enforced(self):
        """
        Check that registration cleanly succeeds with 2FA enabled and enforced
        """

        # Get csrf_token
        self.authenticate(None, None)
        csrf_token = http.Request.csrf_token(self)

        # Values from login form
        name = 'toto'
        payload = {
            'login': 'toto@example.com',
            'name': name,
            'password': 'mypassword',
            'confirm_password': 'mypassword',
            'csrf_token': csrf_token,
        }
        response = self.url_open('/web/signup', data=payload)
        new_user = self.env['res.users'].search([('name', '=', name)])
        self.assertTrue(new_user)
        self.assertEqual(response.status_code, 200, "Signup request should succeed with a 200")
