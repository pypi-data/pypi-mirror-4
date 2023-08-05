from datetime import datetime as dt, timedelta as td
from unittest import skipUnless
from django.test import TestCase
from django.test.utils import override_settings
from django.core.management import call_command
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from zeropass.models import Token
from zeropass.tasks import delete_token


try:
    from celery import task
    has_celery = True
except ImportError:
    has_celery = False


class CleanupTestCases(TestCase):
    """make sure management command and celery task
    are doing their jobs"""


    @skipUnless(has_celery, "requires djcelery")
    @override_settings(ZP_CELERY_CLEANUP=True)
    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_task_via_celery(self):
        """if the task is called via celery it get's deleted"""
        # import conf and force a reload
        from time import sleep
        from zeropass import conf
        reload(conf)
        # create a task
        u = User()
        u.is_active = True
        u.save()
        # create some tokens
        t1 = Token()
        t1.user = u
        t1.expires = dt.now()
        t1.save()
        # sleep for one second
        sleep(1)
        # now we have no Tokens
        self.assertEqual(0, Token.objects.count())

    def test_task(self):
        """the celery task deletes the token"""
        # create a user
        u = User()
        u.is_active = True
        u.save()
        # create some tokens
        t1 = Token()
        t1.user = u
        t1.expires = dt(2011, 1, 1, 1, 1, 1)
        t1.save()
        # now delete it
        delete_token(t1)
        # we have none
        self.assertEqual(0, Token.objects.count())


    def test_task_fails_silent(self):
        """if the token is used before deletion, it fails silently"""
        # create a user
        u = User()
        u.is_active = True
        u.save()
        # create some tokens
        t1 = Token()
        t1.user = u
        t1.expires = dt(2011, 1, 1, 1, 1, 1)
        t1.save()
        t1.delete()
        # now delete it
        delete_token(t1)
        # we have none
        self.assertEqual(0, Token.objects.count())

    def test_task(self):
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
