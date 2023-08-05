from django.conf import settings as dj_settings


CELERY_CLEANUP = getattr(
    dj_settings,
    'ZP_CELERY_CLEANUP',
    False)

EXPIRES = getattr(
    dj_settings,
    'ZP_EXPIRES',
    600)

PROTOCOL = getattr(
    dj_settings,
    'ZP_PROTOCOL',
    'https')

HTML_EMAILS =  getattr(
    dj_settings,
    'ZP_HTML_EMAILS',
    True)

