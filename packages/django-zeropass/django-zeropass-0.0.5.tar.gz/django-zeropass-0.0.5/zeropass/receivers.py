from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.sites.models import Site
from django.template import loader, Context
from zeropass import conf


def send_email(sender, instance, **kwargs):
    """send the email to the person who requested the token"""
    #
    #
    # return if we're in silent mode return
    try:
        if instance.silent:
            return
    except AttributeError:
        pass
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
        'STATIC_URL': settings.STATIC_URL,
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
