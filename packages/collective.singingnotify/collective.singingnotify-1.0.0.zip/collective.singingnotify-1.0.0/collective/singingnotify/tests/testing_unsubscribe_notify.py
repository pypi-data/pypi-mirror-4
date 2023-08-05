# -*- coding: UTF-8 -*-

from email.MIMEText import MIMEText
from zope.component import getUtility, getMultiAdapter, getSiteManager
from zope.app.intid.interfaces import IIntIdRemovedEvent
from zope.interface import implements

from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction, IExecutable
from collective.singingnotify.mail import UnsubscribeNotifyAction, UnsubscribeNotifyAddForm, UnsubscribeNotifyEditForm

from Products.CMFCore.utils import getToolByName

from Products.MailHost.interfaces import IMailHost
from Products.SecureMailHost.SecureMailHost import SecureMailHost

from Products.PloneTestCase.setup import default_user
from collective.singing.interfaces import ISubscription

# basic test structure copied from plone.app.contentrules test_action_mail.py


class DummyEvent(object):
    implements(IIntIdRemovedEvent)

    def __init__(self, object):
        self.object = object


class DummySecureMailHost(SecureMailHost):
    meta_type = 'Dummy secure Mail Host'

    def __init__(self, id):
        self.id = id
        self.sent = []

    def _send(self, mfrom, mto, messageText, debug=False):
        self.sent.append(messageText)


class TestUnsubscribeAction(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Folder', 'target')

    def testRegistered(self):
        element = getUtility(IRuleAction, name='plone.actions.SingingUnsubscribeNotify')
        self.assertEquals('plone.actions.SingingUnsubscribeNotify', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(ISubscription, element.for_)
        self.assertEquals(IIntIdRemovedEvent, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name='plone.actions.SingingUnsubscribeNotify')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                  name=element.addview)
        self.failUnless(isinstance(addview, UnsubscribeNotifyAddForm))
        addview.createAndAdd(data={'subject': 'My Subject',
                                   'source': 'foo@foomail.com',
                                   'dest_addr': 'foo_dest@foomail.com',
                                   'message': 'Hey, Oh!'})

        e = rule.actions[0]
        self.failUnless(isinstance(e, UnsubscribeNotifyAction))
        self.assertEquals('My Subject', e.subject)
        self.assertEquals('foo@foomail.com', e.source)
        self.assertEquals('foo_dest@foomail.com', e.dest_addr)
        self.assertEquals('Hey, Oh!', e.message)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name='plone.actions.SingingUnsubscribeNotify')
        e = UnsubscribeNotifyAction()
        editview = getMultiAdapter((e, self.folder.REQUEST),
                                   name=element.editview)
        self.failUnless(isinstance(editview, UnsubscribeNotifyEditForm))

    def testExecute(self):
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = UnsubscribeNotifyAction()
        e.source = "foo@foomail.com"
        e.dest_addr = "foo_dest@foomail.com"
        e.message = u"User unsubscribed!"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder)), IExecutable)
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("foo@foomail.com", mailSent.get('From'))
        self.assertEqual("foo_dest@foomail.com", mailSent.get('To'))
        self.assertEqual("User unsubscribed!",
                         mailSent.get_payload(decode=True))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUnsubscribeAction))
    return suite
