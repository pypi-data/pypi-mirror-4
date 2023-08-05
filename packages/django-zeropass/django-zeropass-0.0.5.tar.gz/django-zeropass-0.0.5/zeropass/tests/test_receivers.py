from django.test import TestCase
from django.core import mail
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from zeropass.models import Token


class ReceiverTestCaseEmail(TestCase):

    def test_no_email_when_silent(self):
        """when a token is created an email is sent"""
        # create a user
        u = User()
        u.is_active = True
        u.email = 'me@example.com'
        u.save()
        # create a token
        t = Token()
        t.user = u
        t.slient = True
        t.save()
        # now there is one message
        self.assertEqual(0, len(mail.outbox))

    def test_email_sends_when_token_is_created(self):
        """when a token is created an email is sent"""
        # create a user
        u = User()
        u.is_active = True
        u.email = 'me@example.com'
        u.save()
        # create a token
        t = Token()
        t.user = u
        t.save()
        # now there is one message
        self.assertEqual(1, len(mail.outbox))
