# -*- coding: UTF-8 -*-

from email.MIMEText import MIMEText
from zope.component import getUtility, getMultiAdapter, getSiteManager
from zope.component.interfaces import IObjectEvent
from zope.interface import implements

from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction, IExecutable
from collective.contentrules.mailfromfield.actions.mail import MailFromFieldAction
from collective.contentrules.mailfromfield.actions.mail import MailFromFieldEditForm, MailFromFieldAddForm

from Products.CMFCore.utils import getToolByName

from Products.MailHost.interfaces import IMailHost
from Products.SecureMailHost.SecureMailHost import SecureMailHost

from Products.PloneTestCase.setup import default_user


# basic test structure copied from plone.app.contentrules test_action_mail.py


class DummyEvent(object):
    implements(IObjectEvent)

    def __init__(self, object):
        self.object = object


class DummySecureMailHost(SecureMailHost):
    meta_type = 'Dummy secure Mail Host'

    def __init__(self, id):
        self.id = id
        self.sent = []

    def _send(self, mfrom, mto, messageText, debug=False):
        self.sent.append(messageText)


class TestMailAction(ContentRulesTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))
        self.portal.invokeFactory('Folder', 'target', title=unicode('Càrtella', 'utf-8'))
        self.portal.target.invokeFactory('Document', 'd1', title=unicode('Dòcumento', 'utf-8'))
        self.folder = self.portal.target 

    def testRegistered(self):
        element = getUtility(IRuleAction, name='plone.actions.MailFromField')
        self.assertEquals('plone.actions.MailFromField', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)

    def testInvokeAddView(self):
        element = getUtility(IRuleAction, name='plone.actions.MailFromField')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                  name=element.addview)
        self.failUnless(isinstance(addview, MailFromFieldAddForm))

        addview.createAndAdd(data={'subject': 'My Subject',
                                   'source': 'foo@bar.be',
                                   'fieldName': 'foo',
                                   'target': 'object',
                                   'message': 'Hey, Oh!'})

        e = rule.actions[0]
        self.failUnless(isinstance(e, MailFromFieldAction))
        self.assertEquals('My Subject', e.subject)
        self.assertEquals('foo@bar.be', e.source)
        self.assertEquals('foo', e.fieldName)
        self.assertEquals('object', e.target)
        self.assertEquals('Hey, Oh!', e.message)

    def testInvokeEditView(self):
        element = getUtility(IRuleAction, name='plone.actions.MailFromField')
        e = MailFromFieldAction()
        editview = getMultiAdapter((e, self.folder.REQUEST),
                                   name=element.editview)
        self.failUnless(isinstance(editview, MailFromFieldEditForm))


    def testExecuteNoSource(self):
        self.loginAsPortalOwner()
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailFromFieldAction()
        e.message = 'Document created !'
        e.fieldName = 'foo_attr'
        e.target = 'object'
        self.folder.foo_attr = 'member1@dummy.org'
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        self.assertRaises(ValueError, ex)
        # if we provide a site mail address this won't fail anymore
        sm.manage_changeProperties({'email_from_name': 'The Big Boss',
                                    'email_from_address': 'manager@portal.be',
                                    })
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("member1@dummy.org", mailSent.get('To'))
        self.assertEqual("The Big Boss <manager@portal.be>",
                         mailSent.get('From'))
        self.assertEqual("Document created !",
                         mailSent.get_payload(decode=True))


    def testExecuteSimpleByAttribute(self):
        self.loginAsPortalOwner()
        self.folder.foo_attr = 'member1@dummy.org'
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailFromFieldAction()
        e.source = "foo@bar.be"
        e.fieldName = 'foo_attr'
        e.target = 'object'
        e.message = u"Còntènt '${title}' created in ${url} - Section is '${section_name}' (${section_url}) !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("member1@dummy.org", mailSent.get('To'))
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        self.assertEqual("C\xc3\xb2nt\xc3\xa8nt 'D\xc3\xb2cumento' created in http://nohost/plone/target/d1 - "
                         "Section is 'C\xc3\xa0rtella' (http://nohost/plone/target) !",
                         mailSent.get_payload(decode=True))


    def testExecuteTargetByAttribute(self):
        self.loginAsPortalOwner()
        self.folder.d1.foo_attr = 'member1@dummy.org'
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailFromFieldAction()
        e.source = "foo@bar.be"
        e.fieldName = 'foo_attr'
        e.target = 'target'
        e.message = u"Còntènt '${title}' created in ${url} - Section is '${section_name}' (${section_url}) !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("member1@dummy.org", mailSent.get('To'))
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        self.assertEqual("C\xc3\xb2nt\xc3\xa8nt 'D\xc3\xb2cumento' created in http://nohost/plone/target/d1 - "
                         "Section is 'C\xc3\xa0rtella' (http://nohost/plone/target) !",
                         mailSent.get_payload(decode=True))


    def testExecuteSimpleByMethod(self):
        self.loginAsPortalOwner()
        self.folder.setDescription('member1@dummy.org')
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailFromFieldAction()
        e.source = "foo@bar.be"
        e.fieldName = 'Description'
        e.target = 'object'
        e.message = u"Còntènt '${title}' created in ${url} - Section is '${section_name}' (${section_url}) !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("member1@dummy.org", mailSent.get('To'))
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        self.assertEqual("C\xc3\xb2nt\xc3\xa8nt 'D\xc3\xb2cumento' created in http://nohost/plone/target/d1 - "
                         "Section is 'C\xc3\xa0rtella' (http://nohost/plone/target) !",
                         mailSent.get_payload(decode=True))


    def testExecuteTargetByFieldName(self):
        self.loginAsPortalOwner()
        self.folder.d1.setText('member1@dummy.org')
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailFromFieldAction()
        e.source = "foo@bar.be"
        e.fieldName = 'text'
        e.target = 'target'
        e.message = u"Còntènt '${title}' created in ${url} - Section is '${section_name}' (${section_url}) !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("member1@dummy.org", mailSent.get('To'))
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        self.assertEqual("C\xc3\xb2nt\xc3\xa8nt 'D\xc3\xb2cumento' created in http://nohost/plone/target/d1 - "
                         "Section is 'C\xc3\xa0rtella' (http://nohost/plone/target) !",
                         mailSent.get_payload(decode=True))


    def testExecuteSimpleByCMFProperty(self):
        self.loginAsPortalOwner()
        self.folder.manage_addProperty('foo_property', 'member1@dummy.org', 'string')
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailFromFieldAction()
        e.source = "foo@bar.be"
        e.fieldName = 'foo_property'
        e.target = 'object'
        e.message = u"Còntènt '${title}' created in ${url} - Section is '${section_name}' (${section_url}) !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)),
                             IExecutable)
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("member1@dummy.org", mailSent.get('To'))
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        self.assertEqual("C\xc3\xb2nt\xc3\xa8nt 'D\xc3\xb2cumento' created in http://nohost/plone/target/d1 - "
                         "Section is 'C\xc3\xa0rtella' (http://nohost/plone/target) !",
                         mailSent.get_payload(decode=True))


    def testExecuteFolderModify(self):
        # can happen as rules are not triggered on the rule root itself
        self.loginAsPortalOwner()
        self.folder.foo_property = 'member1@dummy.org'
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        e = MailFromFieldAction()
        e.source = "foo@bar.be"
        e.fieldName = 'foo_property'
        e.target = 'object'
        e.message = u"Còntènt '${title}' created in ${url} - Section is '${section_name}' (${section_url}) !"
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder)),
                             IExecutable)
        ex()
        self.failUnless(isinstance(dummyMailHost.sent[0], MIMEText))
        mailSent = dummyMailHost.sent[0]
        self.assertEqual('text/plain; charset="utf-8"',
                        mailSent.get('Content-Type'))
        self.assertEqual("member1@dummy.org", mailSent.get('To'))
        self.assertEqual("foo@bar.be", mailSent.get('From'))
        self.assertEqual("C\xc3\xb2nt\xc3\xa8nt 'C\xc3\xa0rtella' created in http://nohost/plone/target - "
                         "Section is 'C\xc3\xa0rtella' (http://nohost/plone/target) !",
                         mailSent.get_payload(decode=True))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMailAction))
    return suite
