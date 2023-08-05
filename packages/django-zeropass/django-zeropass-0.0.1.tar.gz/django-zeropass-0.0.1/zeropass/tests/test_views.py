from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from zeropass.models import Token


class ViewTestCases(TestCase):

    def test_sent_200_get(self):
        """the sent returns 200 on get"""
        r = self.client.get(reverse('zeropass:sent'))
        # 200
        self.assertEqual(200, r.status_code)

    def test_login_200_get(self):
        """the logn returns 200 on get"""
        r = self.client.get(reverse('zeropass:login'))
        # 200
        self.assertEqual(200, r.status_code)

    def test_login_200_post(self):
        """the logn returns 200 on post"""
        r = self.client.post(reverse('zeropass:login'), {})
        # 200
        self.assertEqual(200, r.status_code)

    def test_login_200_post_invalid(self):
        """the logn returns a 302  on posti when valid date is sent"""
        # we have no tokens
        self.assertEqual(0, Token.objects.count())
        # send valid date
        r = self.client.post(
            reverse('zeropass:login'),
            {'email': 'me@example.com'})
        # 200 
        self.assertEqual(200, r.status_code)
        # we now have no token
        self.assertEqual(0, Token.objects.count())

    def test_login_200_post_valid(self):
        """the logn returns a 302  on posti when valid date is sent"""
        # create a user
        u = User()
        u.is_active = True
        u.email = 'me@example.com'
        u.save()
        # we have no tokens
        self.assertEqual(0, Token.objects.count())
        # send valid date
        r = self.client.post(
            reverse('zeropass:login'),
            {'email': 'me@example.com'})
        # 302
        self.assertEqual(302, r.status_code)
        # we now have one token
        self.assertEqual(1, Token.objects.count())

    def test_validate_user_has_to_be_active(self):
        """if a user is not active they are redirected to login"""
        u = User()
        u.is_active = False
        u.email = 'me@example.com'
        u.save()
        # make token
        t = Token()
        t.next = '/'
        t.user = u
        t.save()
        # call view and we're logged in
        r = self.client.get(reverse('zeropass:validate', args=[t.token]))
        # we were redirect to '/'
        self.assertRedirects(r, reverse('zeropass:login'))


    def test_validate_valid(self):
        """when validate is passed a valid token a user is logged in"""
        # make user
        u = User()
        u.is_active = True
        u.email = 'me@example.com'
        u.save()
        # make token
        t = Token()
        t.next = '/'
        t.user = u
        t.save()
        # call view and we're logged in
        r = self.client.get(reverse('zeropass:validate', args=[t.token]))
        # we were redirect to '/'
        self.assertRedirects(r, '/')


    def test_validate_invalid_token(self):
        # invalid tokens results in a 404
        r = self.client.get(
                reverse('zeropass:validate', args=['a' * 40]))
        # we have a 404
        self.assertEqual(404, r.status_code)
