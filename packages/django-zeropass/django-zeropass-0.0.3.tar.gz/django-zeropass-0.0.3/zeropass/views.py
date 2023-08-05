from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as dj_login
from django.http import HttpResponseRedirect, Http404
from django.conf import settings
from zeropass.models import Token
from zeropass.forms import TokenForm


def login(request):
    """processes or displays a form depending on
    whether or not post data is present"""
    initial = {'next': request.GET.get('next')}
    form = TokenForm(
        request.POST or None,
        initial=initial)

    if form.is_valid():
        token = form.save()
        return HttpResponseRedirect(
            reverse('zeropass:sent'))

    return render(
        request,
        'zeropass/login.html',
        {'form': form})


def sent(request):
    """display a nice done type page"""
    return render(
        request,
        'zeropass/sent.html')


def validate(request, token):
    """validates a token and if it is valid it will
    login the user in"""
    # get the token or 404
    try:
        t = Token.objects.get(token=token)
    except Token.DoesNotExist:
        raise Http404('not matching token could be found')
    # attempt to get the user
    user = authenticate(token=token)
    # if we had a user returned
    if user is not None:
        # if user is active log in and redirect if token next
        if user.is_active:
            # log te user in
            dj_login(request, user)
            # set up redirect
            url = t.next or settings.LOGIN_REDIRECT_URL
            # delete the token
            t.delete()
            # return the redirect
            return HttpResponseRedirect(url)
    # redirect to login
    return HttpResponseRedirect(reverse('zeropass:login'))
