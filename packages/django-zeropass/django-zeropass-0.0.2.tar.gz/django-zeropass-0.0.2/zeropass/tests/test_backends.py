from datetime import datetime as dt, timedelta as td
from django.test import TestCase
from django.contrib.auth import authenticate, login as dj_login
from django.contrib.auth.models import User
from zeropass.models import Token
from zeropass.backends import TokenBackend


class BackendTestCases(TestCase):

    def test_get_user_exist(self):
        """get_user() returns a user"""
        u = User()
        u.is_active = True
        u.email = 'me@example.com'
        u.save()
        # make backend
        tb = TokenBackend()
        user = tb.get_user(u.id)
        # user is same as u
        self.assertEqual(user.id, u.id)

    def test_get_user_not_exist(self):
        """get_user() returns a user"""
        # make backend
        tb = TokenBackend()
        user = tb.get_user(8)
        # user is None
        self.assertEqual(user, None)

    def test_no_match(self):
        """If no match is found then None is returned"""
        # make a fake token
        fake_token = 'a' * 40
        user = authenticate(token=fake_token)
        # user is None
        self.assertEqual(None, user)

    def test_no_match_expired(self):
        """if a token is expired no match is return"""
        # make a user
        u = User()
        u.is_active = True
        u.email = 'me@example.com'
        u.save()
        # make a token with expires in past
        t = Token()
        t.expires = dt.now() - td(seconds=300)
        t.user = u
        t.save()
        # send te tokem through the backend and get user back
        user = authenticate(token=t.token)
        # user is None
        self.assertEqual(user, None)

    def test_match(self):
        """the backend returns the user when a match is found"""
        # make a user
        u = User()
        u.is_active = True
        u.email = 'me@example.com'
        u.save()
        # make a token
        t = Token()
        t.user = u
        t.save()
        # send te tokem through the backend and get user back
        user = authenticate(token=t.token)
        # user the save as above
        self.assertEqual(user.pk, u.pk)
