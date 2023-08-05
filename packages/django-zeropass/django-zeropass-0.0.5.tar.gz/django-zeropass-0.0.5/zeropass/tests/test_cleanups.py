from datetime import datetime as dt, timedelta as td
from unittest import skipUnless
from django.db.models import signals
from django.test import TestCase
from django.test.utils import override_settings
from django.core.management import call_command
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from zeropass.models import Token
from zeropass import receivers


class CleanupTestCases(TestCase):
    """make sure management command and celery task
    are doing their jobs"""

    def test_command(self):
        """the management command deletes expired tokens"""
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
        t3 = Token()
        t3.user = u
        t3.expires = dt(2013, 1, 1, 1, 1, 1)
        t3.save()
        # call the managemet command
        call_command('zeropass_cleanup')
        # we have none
        self.assertEqual(1, Token.objects.count())
