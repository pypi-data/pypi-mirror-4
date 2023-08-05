from django.conf import settings as dj_settings


EXPIRES = getattr(
    dj_settings,
    'ZP_EXPIRES',
    600)

PROTOCOL = getattr(
    dj_settings,
    'ZP_PROTOCOL',
    'https')

HTML_EMAILS = getattr(
    dj_settings,
    'ZP_HTML_EMAILS',
    True)
