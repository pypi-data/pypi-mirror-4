from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from zope.component import adapts
from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface, implements
from zope.formlib import form
from zope import schema

from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable

from Products.CMFCore.utils import getToolByName
from collective.singingnotify import MessageFactory as _
from collective.singingnotify import logger


class IUnsubscribeNotifyAction(Interface):
    """Definition of the configuration available for a mail action
    """
    subject = schema.TextLine(
        title=_(u"Subject"),
        description=_(u"Subject of the message"),
        required=True
        )

    source = schema.TextLine(
        title=_(u"Sender email"),
        description=_("The email address that sends the email. If no email is \
            provided here, it will use the portal from address."),
         required=False
         )

    dest_addr = schema.TextLine(
        title=_(u"Receiver email"),
        description=_("The address where you want to send the e-mail message."),
        required=True
        )

    message = schema.Text(
        title=_(u"Message"),
        description=_(u"Type in here the message that you want to mail. Some \
            defined content can be replaced: ${portal} will be replaced by the title \
            of the portal. ${url} will be replaced by the URL of the newsletter. \
            ${channel} will be replaced by the newsletter channel name. ${subscriber} will be replaced by subscriber name."),
        required=True
        )


class UnsubscribeNotifyAction(SimpleItem):
    """
    The implementation of the action defined before
    """
    implements(IUnsubscribeNotifyAction, IRuleElementData)

    subject = u''
    source = u''
    dest_addr = u''
    message = u''

    element = 'plone.actions.SingingUnsubscribeNotify'

    @property
    def summary(self):
        return _(u"Email report to ${dest_addr}",
                 mapping=dict(dest_addr=self.dest_addr))


class MailActionExecutor(object):
    """
    The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IUnsubscribeNotifyAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        mailhost = getToolByName(aq_inner(self.context), "MailHost")
        if not mailhost:
            raise ComponentLookupError, 'You must have a Mailhost utility to \
execute this action'
        source = self.element.source
        dest_addr = self.element.dest_addr
        urltool = getToolByName(aq_inner(self.context), "portal_url")
        portal = urltool.getPortalObject()
        email_charset = portal.getProperty('email_charset')
        if not source:
            # no source provided, looking for the site wide from email
            # address
            from_address = portal.getProperty('email_from_address')
            if not from_address:
                raise ValueError, 'You must provide a source address for this \
action or enter an email in the portal properties'
            from_name = portal.getProperty('email_from_name')
            source = "%s <%s>" % (from_name, from_address)

        obj = self.event.object
        folder_url = self.context.absolute_url()
        channel = getattr(obj, 'channel', None)
        composer_data = getattr(obj, 'composer_data', None)
        message = self.element.message
        message = message.replace("${url}", folder_url)
        message = message.replace("${portal}", portal.Title())
        if channel:
            message = message.replace("${channel}", channel.title)
        if composer_data:
            message = message.replace("${subscriber}", composer_data.get('email', ''))
        subject = self.element.subject
        subject = subject.replace("${url}", folder_url)
        subject = subject.replace("${portal}", portal.Title())
        logger.info('sending to: %s' % dest_addr)
        try:
            # sending mail in Plone 4
            mailhost.send(message, mto=dest_addr, mfrom=source,
                    subject=subject, charset=email_charset)
        except:
            #sending mail in Plone 3
            mailhost.secureSend(message, dest_addr, source,
                    subject=subject, subtype='plain',
                    charset=email_charset, debug=False)

        return True


class UnsubscribeNotifyAddForm(AddForm):
    """
    An add form for the mail action
    """
    form_fields = form.FormFields(IUnsubscribeNotifyAction)
    label = _(u"Add S&D Unsubscription Mail Action")
    description = _(u"A mail action that sends email notify when an user will unsubscribe from a channel.")
    form_name = _(u"Configure element")

    def create(self, data):
        a = UnsubscribeNotifyAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class UnsubscribeNotifyEditForm(EditForm):
    """
    An edit form for the mail action
    """
    form_fields = form.FormFields(IUnsubscribeNotifyAction)
    label = _(u"Edit S&D Unsubscription Mail Action")
    description = _(u"A mail action that sends email notify when an user will unsubscribe from a channel.")
    form_name = _(u"Configure element")
