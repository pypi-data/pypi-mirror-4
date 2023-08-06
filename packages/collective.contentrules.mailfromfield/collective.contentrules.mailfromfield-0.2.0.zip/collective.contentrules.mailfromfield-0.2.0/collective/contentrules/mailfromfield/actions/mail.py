# -*- coding: utf-8 -*-

import logging

from Acquisition import aq_inner, aq_base
from OFS.SimpleItem import SimpleItem
from zope.component import adapts
from zope.component.interfaces import ComponentLookupError
from zope.interface import Interface, implements
from zope.formlib import form
from zope import schema

from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.app.vocabularies.groups import GroupsSource
from plone.app.vocabularies.users import UsersSource
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from collective.contentrules.mailfromfield import messageFactory as _

class IMailFromFieldAction(Interface):
    """Definition of the configuration available for a mail action
    """
    subject = schema.TextLine(
        title = _(u"Subject"),
        description = _(u"Subject of the message"),
        required = True
        )

    source = schema.TextLine(
        title = _(u"Sender email"),
        description = _(u"The email address that sends the email. If no email is "
                         "provided here, it will use the portal from address."),
         required = False
         )

    fieldName = schema.TextLine(
        title = _(u"Source field"),
        description = _(u"Put there the field name from which get the e-mail. "
                         "You can provide an attribute name, a method name, an AT field name or "
                         "ZMI property"),
         required = True
         )

    target = schema.Choice(
        required=True,
        title=_(u"Target element"),
        description=_('help_target',
                      default=u"Choose to get the address info from the content where the rule is activated on "
                              u"or from the target element of the event."
                      ),
        default='object',
        vocabulary='collective.contentrules.mailfromfield.vocabulary.targetElements',
        )

    message = schema.Text(
        title = _(u"Mail message"),
        description = _('help_message',
                        default=u"Type in here the message that you want to mail. Some "
                                 "defined content can be replaced: ${title} will be replaced by the title "
                                 "of the target item. ${url} will be replaced by the URL of the item. "
                                 "${section_url} will be replaced by the URL of the content the rule is applied to. "
                                 "${section_name} will be replaced by the title of the content the rule is applied "
                                 "to."),
        required = True
        )


class MailFromFieldAction(SimpleItem):
    """
    The implementation of the action defined before
    """
    implements(IMailFromFieldAction, IRuleElementData)

    subject = u''
    source = u''
    fieldName = u''
    target=u''
    message = u''

    element = 'plone.actions.MailFromField'

    @property
    def summary(self):
        return _('action_summary',
                 default=u'Email to users defined in the "${fieldName}" data',
                 mapping=dict(fieldName=self.fieldName))


class MailActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IMailFromFieldAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        context = self.context
        element = self.element
        event = self.event
        recipients = []      
        
        target = element.target
        if target=='object':
            obj = context
        else: # target
            obj = event.object

        mailhost = getToolByName(aq_inner(self.context), "MailHost")
        if not mailhost:
            raise ComponentLookupError, 'You must have a Mailhost utility to execute this action'

        source = element.source
        urltool = getToolByName(aq_inner(self.context), "portal_url")
        portal = urltool.getPortalObject()
        email_charset = portal.getProperty('email_charset')
        if not source:
            # no source provided, looking for the site wide "from" email address
            from_address = portal.getProperty('email_from_address')
            if not from_address:
                raise ValueError, ('You must provide a source address for this '
                                   'action or enter an email in the portal properties')
            from_name = portal.getProperty('email_from_name')
            source = "%s <%s>" % (from_name, from_address)

        obj_title = safe_unicode(event.object.Title())
        section_title = safe_unicode(context.Title())
        event_url = event.object.absolute_url()
        message = self.element.message.replace("${url}", event_url)
        message = message.replace("${title}", obj_title)
        message = message.replace("${section_name}", section_title)
        message = message.replace("${section_url}", context.absolute_url())

        subject = self.element.subject.replace("${url}", event_url)
        subject = subject.replace("${title}", obj_title)
        subject = subject.replace("${section_name}", section_title)
        subject = subject.replace("${section_url}", context.absolute_url())

        obj = aq_base(aq_inner(obj))

        logger = logging.getLogger('collective.contentrules.mailfromfield')
        
        # Try to load data from the target object
        fieldName = str(element.fieldName)
        # 1: object attribute
        try:
            attr = obj.__getattribute__(fieldName)
            # 3: object method
            if hasattr(attr, '__call__'):
                recipients = attr()
                logger.debug('getting e-mail from %s method' % fieldName)
            else:
                recipients = attr
                logger.debug('getting e-mail from %s attribute' % fieldName)
        except AttributeError:
            # 2: try with AT field
            if obj.getField(fieldName):
                recipients = obj.getField(fieldName).get(obj)
            if not recipients:
                recipients = obj.getProperty(fieldName, [])
                if recipients:
                    logger.debug('getting e-mail from %s CMF property' % fieldName)
            else:
                logger.debug('getting e-mail from %s AT field' % fieldName)

        # now tranform recipients in a iterator, if needed
        if type(recipients) == str or type(recipients) == unicode:
            recipients = [str(recipients),]

        for email_recipient in recipients:
            logger.debug('sending to: %s' % email_recipient)

            try: # sending mail in Plone 4
                mailhost.send(message, mto=email_recipient, mfrom=source,
                              subject=subject, charset=email_charset)
            except: #sending mail in Plone 3
                mailhost.secureSend(message, email_recipient, source,
                                    subject=subject, subtype='plain',
                                    charset=email_charset, debug=False,
                                    From=source)

        return True


class MailFromFieldAddForm(AddForm):
    """
    An add form for the mail action
    """
    form_fields = form.FormFields(IMailFromFieldAction)
    label = _(u"Add mail from field action")
    description = _(u"A mail action that take the e-mail address from the content where the rule is activated.")
    form_name = _(u"Configure element")

    def create(self, data):
        a = MailFromFieldAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class MailFromFieldEditForm(EditForm):
    """
    An edit form for the mail action
    """
    form_fields = form.FormFields(IMailFromFieldAction)
    label = _(u"Add mail from field action")
    description = _(u"A mail action that take the e-mail address from the content where the rule is activated.")
    form_name = _(u"Configure element")
