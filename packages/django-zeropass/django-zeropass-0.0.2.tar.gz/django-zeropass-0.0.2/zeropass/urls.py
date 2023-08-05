from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
    url(
        r'^$',
        'zeropass.views.login',
        name='login'),
    url(
        r'^(?P<token>\w{40})',
        'zeropass.views.validate',
        name='validate'),
    url(
        r'^sent/$',
        'zeropass.views.sent',
        name='sent'),
)
