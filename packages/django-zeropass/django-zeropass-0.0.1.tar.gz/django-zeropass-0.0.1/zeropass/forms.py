import hashlib
from datetime import datetime, timedelta
from django import forms
from django.contrib.auth.models import User
from zeropass.models import Token
from zeropass import conf



class TokenForm(forms.Form):

    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            self.user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError('Email not found')
        return email

    def save(self):
       token = Token()
       token.user = self.user
       token.expires = datetime.now() + timedelta(seconds=conf.EXPIRES)
       token.save()
