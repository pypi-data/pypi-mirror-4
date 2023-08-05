from string import letters
from datetime import datetime
from hashlib import sha1
from random import choice
from datetime import datetime as dt, timedelta as td
from django.db import models
from django.contrib.auth.models import User
from zeropass import conf
from zeropass import receivers


class TokenManager(models.Manager):

    def expired(self):
        return super(TokenManager, self).get_query_set()\
            .filter(expires__lt=datetime.now())


class Token(models.Model):
    user = models.ForeignKey(
            User)
    token = models.CharField(
            blank=True,
            null=True,
            max_length=40)
    expires = models.DateTimeField()
    next = models.CharField(
            max_length=255,
            blank=True,
            null=True)

    objects = TokenManager()

    def __unicode__(self):
        return '<Token for %s>' % self.user.username

    def save(self, *args, **kwargs):
        # set the expires
        if self.expires is None:
            self.expires = dt.now() + td(seconds=conf.EXPIRES)
        # set the token
        if self.token == None or self.token == '':
            seed = ''.join(choice(letters) for x in range(10))
            self.token = sha1(seed).hexdigest()
        super(Token, self).save(*args, **kwargs)
#
#
# connect the receivers
models.signals.post_save.connect(
        receivers.set_deletion_task,
        sender=Token,
        dispatch_uid='receivers_set_deletion_task')
#
#
# connect the receivers
models.signals.post_save.connect(
        receivers.send_email,
        sender=Token,
        dispatch_uid='receivers_send_email')
