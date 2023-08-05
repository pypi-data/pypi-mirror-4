from datetime import datetime
from django.contrib.auth.models import User
from zeropass.models import Token


class TokenBackend(object):

    def authenticate(self, **kwargs):
        try:
            # get the token
            token = Token.objects.get(
                token=kwargs['token'],
                expires__gt=datetime.now())
            # get the user
            return token.user
        except (KeyError, Token.DoesNotExist):
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
