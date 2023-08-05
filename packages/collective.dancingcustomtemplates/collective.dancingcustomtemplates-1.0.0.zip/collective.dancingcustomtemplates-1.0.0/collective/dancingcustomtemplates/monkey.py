from collective.dancing import utils
from collective.dancing import MessageFactory as _
from zope.i18n import translate
import string
from zope.app.component.hooks import getSite
from collective.dancing.composer import template_var
from collective.singing.mail import create_html_mail
from collective.singing.message import Message


def render_confirmation(self, subscription):
    """
    Custom render_confirmation method.
    If there is a registered template with id "confirm_newsletter_subscription" use it.
    If there isn't, use the default template.
    """
    vars = self._vars(subscription)
    subscription_vars = self._subscription_vars(subscription)

    if 'confirmation_subject' not in vars:
        vars['confirmation_subject'] = translate(
            _(u"Confirm your subscription with ${channel-title}",
              mapping={'channel-title': subscription.channel.title}),
            target_language=self.language)
    to_addr = subscription_vars[template_var('to_addr')]
    vars['to_addr'] = to_addr
    portal = getSite()
    confirm_template = portal.restrictedTraverse('confirm_newsletter_subscription',
                                               self.confirm_template)
    html = confirm_template(**vars)
    html = utils.compactify(html)
    html = string.Template(html).safe_substitute(subscription_vars)

    message = create_html_mail(
        vars['confirmation_subject'],
        html,
        from_addr=vars['from_addr'],
        to_addr=to_addr,
        headers=vars.get('more_headers'),
        encoding=self.encoding)

    # status=None prevents message from ending up in any queue
    return Message(
        message, subscription, status=None)


def render_forgot_secret(self, subscription):
    """
    Custom render_forgot method.
    If there is a registered template with id "forgot_newsletter_subscription" use it.
    If there isn't, use the default template.
    """
    vars = self._vars(subscription)
    subscription_vars = self._subscription_vars(subscription)
    portal = getSite()
    if 'forgot_secret_subject' not in vars:
        vars['forgot_secret_subject'] = translate(
            _(u"Change your subscriptions with ${site_title}",
              mapping={'site_title': vars['channel_title']}),
            target_language=self.language)
    forgot_template = portal.restrictedTraverse('forgot_newsletter_subscription',
                                           self.forgot_template)
    html = forgot_template(**vars)
    html = utils.compactify(html)
    html = string.Template(html).safe_substitute(subscription_vars)

    message = create_html_mail(
        vars['forgot_secret_subject'],
        html,
        from_addr=vars['from_addr'],
        to_addr=subscription_vars[template_var('to_addr')],
        headers=vars.get('more_headers'),
        encoding=self.encoding)

    # status=None prevents message from ending up in any queue
    return Message(
        message, subscription, status=None)
