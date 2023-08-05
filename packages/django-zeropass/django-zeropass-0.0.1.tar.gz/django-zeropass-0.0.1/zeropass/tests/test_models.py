from datetime import datetime as dt
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from zeropass.models import Token


class ManagerTestCases(TestCase):

    def test_expired(self):
        """The expired manager returns expired tokens"""
        # create a user
        u = User()
        u.is_active = True
        u.save()
        # create some tokens
        t1 = Token()
        t1.user = u
        t1.expires = dt(2011, 1, 1, 1, 1, 1)
        t1.save()
        t2 = Token()
        t2.user = u
        t2.expires = dt(2011, 1, 1, 1, 1, 1)
        t2.save()
        # expired returns 2
        self.assertEqual(2, Token.objects.expired().count())
        # update t2
        t2.expires = dt(2013, 1, 1, 1, 1, 1)
        t2.save()
        # now we have only one expired
        self.assertEqual(1, Token.objects.expired().count())


class ModelTestCases(TestCase):


    def test_token_when_saved(self):
        """when a token is saved it get's a random token"""
        u = User()
        u.is_active = True
        u.save()
        # make a token
        t = Token()
        t.user = u
        t.save()
        # the token now has a 40 digit token
        self.assertEqual(40, len(t.token))

    def test_expires_when_save(self):
        """when a token is saved it get's a random token"""
        u = User()
        u.is_active = True
        u.save()
        # make a token
        t = Token()
        t.user = u
        # the token has no
        self.assertFalse(t.expires)
        # save it
        t.save()
        # the token now has an expiry
        self.assertTrue(t.expires)
