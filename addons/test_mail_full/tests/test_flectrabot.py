# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch

from flectra.addons.mail.tests.common import MailCommon
from flectra.addons.test_mail.tests.common import TestRecipients
from flectra.tests import tagged
from flectra.tools import mute_logger


@tagged("flectrabot")
class TestFlectrabot(MailCommon, TestRecipients):

    @classmethod
    def setUpClass(cls):
        super(TestFlectrabot, cls).setUpClass()
        cls.test_record = cls.env['mail.test.simple'].with_context(cls._test_context).create({'name': 'Test', 'email_from': 'ignasse@example.com'})

        cls.flectrabot = cls.env.ref("base.partner_root")
        cls.message_post_default_kwargs = {
            'body': '',
            'attachment_ids': [],
            'message_type': 'comment',
            'partner_ids': [],
            'subtype_xmlid': 'mail.mt_comment'
        }
        cls.flectrabot_ping_body = '<a href="http://flectrahq.com/web#model=res.partner&amp;id=%s" class="o_mail_redirect" data-oe-id="%s" data-oe-model="res.partner" target="_blank">@FlectraBot</a>' % (cls.flectrabot.id, cls.flectrabot.id)
        cls.test_record_employe = cls.test_record.with_user(cls.user_employee)

    @mute_logger('flectra.addons.mail.models.mail_mail')
    def test_fetch_listener(self):
        channel = self.user_employee.with_user(self.user_employee)._init_flectrabot()
        flectrabot = self.env.ref("base.partner_root")
        flectrabot_in_fetch_listeners = self.env['discuss.channel.member'].search([('channel_id', '=', channel.id), ('partner_id', '=', flectrabot.id)])
        self.assertEqual(len(flectrabot_in_fetch_listeners), 1, 'flectrabot should appear only once in channel_fetch_listeners')

    @mute_logger('flectra.addons.mail.models.mail_mail')
    def test_flectrabot_ping(self):
        kwargs = self.message_post_default_kwargs.copy()
        kwargs.update({'body': self.flectrabot_ping_body, 'partner_ids': [self.flectrabot.id, self.user_admin.partner_id.id]})

        with patch('random.choice', lambda x: x[0]):
            self.assertNextMessage(
                self.test_record_employe.with_context({'mail_post_autofollow': True}).message_post(**kwargs),
                sender=self.flectrabot,
                answer=False
            )
        # Flectrabot should not be a follower but user_employee and user_admin should
        follower = self.test_record.message_follower_ids.mapped('partner_id')
        self.assertNotIn(self.flectrabot, follower)
        self.assertIn(self.user_employee.partner_id, follower)
        self.assertIn(self.user_admin.partner_id, follower)

    @mute_logger('flectra.addons.mail.models.mail_mail')
    def test_onboarding_flow(self):
        kwargs = self.message_post_default_kwargs.copy()
        channel = self.user_employee.with_user(self.user_employee)._init_flectrabot()

        kwargs['body'] = 'tagada 😊'
        last_message = self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.flectrabot,
            answer=("help",)
        )
        channel.execute_command_help()
        self.assertNextMessage(
            last_message,  # no message will be post with command help, use last flectrabot message instead
            sender=self.flectrabot,
            answer=("@FlectraBot",)
        )
        kwargs['body'] = ''
        kwargs['partner_ids'] = [self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")]
        self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.flectrabot,
            answer=("attachment",)
        )
        kwargs['body'] = ''
        attachment = self.env['ir.attachment'].with_user(self.user_employee).create({
            'datas': 'bWlncmF0aW9uIHRlc3Q=',
            'name': 'picture_of_your_dog.doc',
            'res_model': 'mail.compose.message',
        })
        kwargs['attachment_ids'] = [attachment.id]
        # For the end of the flow, we only test that the state changed, but not to which
        # one since it depends on the intalled apps, which can add more steps (like livechat)
        channel.message_post(**kwargs)
        self.assertNotEqual(self.user_employee.flectrabot_state, 'onboarding_attachement')

        # Test miscellaneous messages
        self.user_employee.flectrabot_state = "idle"
        kwargs['partner_ids'] = []
        kwargs['body'] = "I love you"
        self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.flectrabot,
            answer=("too human for me",)
        )
        kwargs['body'] = "Go fuck yourself"
        self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.flectrabot,
            answer=("I have feelings",)
        )
        kwargs['body'] = "help me"
        self.assertNextMessage(
            channel.message_post(**kwargs),
            sender=self.flectrabot,
            answer=("If you need help",)
        )

    @mute_logger('flectra.addons.mail.models.mail_mail')
    def test_flectrabot_no_default_answer(self):
        kwargs = self.message_post_default_kwargs.copy()
        kwargs.update({'body': "I'm not talking to @flectrabot right now", 'partner_ids': []})
        self.assertNextMessage(
            self.test_record_employe.message_post(**kwargs),
            answer=False
        )

    def assertNextMessage(self, message, answer=None, sender=None):
        last_message = self.env['mail.message'].search([('id', '=', message.id + 1)])
        if last_message:
            body = last_message.body.replace('<p>', '').replace('</p>', '')
        else:
            self.assertFalse(answer, "No last message found when an answer was expect")
        if answer is not None:
            if answer and not last_message:
                self.assertTrue(False, "No last message found")
            if isinstance(answer, list):
                self.assertIn(body, answer)
            elif isinstance(answer, tuple):
                for elem in answer:
                    self.assertIn(elem, body)
            elif not answer:
                self.assertFalse(last_message, "No answer should have been post")
                return
            else:
                self.assertEqual(body, answer)
        if sender:
            self.assertEqual(sender, last_message.author_id)
        return last_message
