from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.sites.models import Site
from django.template import loader, Context
from zeropass import conf
# only import the tasks if djcelery is in installed apps
if 'djcelery' in settings.INSTALLED_APPS:
    from zeropass.tasks import delete_token

def set_deletion_task(sender, instance, **kwargs):
    """set a token to be deleted by a task rather than management
    command"""
    if conf.CELERY_CLEANUP:
        delete_token.apply_async((instance,), eta=instance.expires)
        

def send_email(sender, instance, **kwargs):
    """send the email to the person who requested the token"""
    #
    #
    # the site
    site = Site.objects.get_current()
    #
    #
    # the subjects
    subject = kwargs.get('subject') or '%s login' % site.name
    #
    #
    # the context
    c = Context({
        'token': instance,
        'site': site,
        'protocol': conf.PROTOCOL
    })
    #
    #
    # generate the text content
    t = loader.get_template('zeropass/email.txt')
    text_content = t.render(c)
    #
    #
    # build the message
    msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email])
    #
    #
    # if we're sending HTML
    if conf.HTML_EMAILS:
        #
        #
        # generate the html content
        t = loader.get_template('zeropass/email.html')
        html_content = t.render(c)
        msg.attach_alternative(html_content, "text/html")
    #
    #
    # now send it
    msg.send()
