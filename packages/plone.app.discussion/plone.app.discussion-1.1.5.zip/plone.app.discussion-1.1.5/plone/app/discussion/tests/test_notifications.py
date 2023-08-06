# coding=utf-8

import unittest

from Acquisition import aq_base

from zope.component import createObject
from zope.component import getSiteManager
from zope.component import queryUtility

from Products.PloneTestCase.ptc import PloneTestCase

from Products.MailHost.interfaces import IMailHost
from Products.CMFPlone.tests.utils import MockMailHost

from plone.registry.interfaces import IRegistry

from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.tests.layer import DiscussionLayer


class TestUserNotificationUnit(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        # Set up a mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

        # We need to fake a valid mail setup
        self.portal.email_from_address = "portal@plone.test"
        self.mailhost = self.portal.MailHost

        # Enable user notification setting
        registry = queryUtility(IRegistry)
        registry['plone.app.discussion.interfaces.IDiscussionSettings' +
                 '.user_notification_enabled'] = True

        # Create test content
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Document', 'doc1')
        self.portal_discussion = self.portal.portal_discussion
        # Archetypes content types store data as utf-8 encoded strings
        # The missing u in front of a string is therefor not missing
        self.portal.doc1.title = 'Kölle Alaaf' # What is "Fasching"?
        self.conversation = IConversation(self.portal.doc1)

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)

    def test_notify_user(self):
        # Add a comment with user notification enabled. Add another comment
        # and make sure an email is send to the user of the first comment.
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.user_notification = True
        comment.author_email = "john@plone.test"
        self.conversation.addComment(comment)

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        self.conversation.addComment(comment)
        self.assertEquals(len(self.mailhost.messages), 1)
        self.failUnless(self.mailhost.messages[0])
        msg = str(self.mailhost.messages[0])
        self.failUnless('To: john@plone.test' in msg)
        self.failUnless('From: portal@plone.test' in msg)

        # We expect the headers to be properly header encoded (7-bit):
        #>>> 'Subject: =?utf-8?q?Some_t=C3=A4st_subject=2E?=' in msg
        #True
#        # The output should be encoded in a reasonable manner
        # (in this case quoted-printable):
        #>>> msg
        #'...Another t=C3=A4st message...You are receiving this mail \
        #because T=C3=A4st user\ntest@plone.test...is sending feedback \
        #about the site you administer at...

    def test_do_not_notify_user_when_notification_is_disabled(self):
        # Disable user notification and make sure no email is send to the user.
        registry = queryUtility(IRegistry)
        registry['plone.app.discussion.interfaces.IDiscussionSettings.' +
                  'user_notification_enabled'] = False

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.user_notification = True
        comment.author_email = "john@plone.test"
        self.conversation.addComment(comment)

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        self.conversation.addComment(comment)

        self.assertEquals(len(self.mailhost.messages), 0)

    def test_do_not_notify_user_when_email_address_is_given(self):
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.user_notification = True
        self.conversation.addComment(comment)

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        self.conversation.addComment(comment)

        self.assertEquals(len(self.mailhost.messages), 0)

    def test_do_not_notify_user_when_no_sender_is_available(self):
        # Set sender mail address to none and make sure no email is send to
        # the moderator.
        self.portal.email_from_address = None

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.user_notification = True
        comment.author_email = "john@plone.test"
        self.conversation.addComment(comment)

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        self.conversation.addComment(comment)

        self.assertEquals(len(self.mailhost.messages), 0)

    def test_notify_only_once(self):
        # When a user has added two comments in a conversation and has
        # both times requested email notification, do not send him two
        # emails when another comment has been added.

        # Comment 1
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.user_notification = True
        comment.author_email = "john@plone.test"
        self.conversation.addComment(comment)

        # Comment 2
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        comment.user_notification = True
        comment.author_email = "john@plone.test"
        self.conversation.addComment(comment)
        # Note that we might want to get rid of this message, as the
        # new comment is added by the same user.
        self.assertEquals(len(self.mailhost.messages), 1)
        self.mailhost.reset()
        self.assertEquals(len(self.mailhost.messages), 0)

        # Comment 3
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        self.conversation.addComment(comment)
        self.assertEquals(len(self.mailhost.messages), 1)
        self.failUnless(self.mailhost.messages[0])
        msg = str(self.mailhost.messages[0])
        self.failUnless('To: john@plone.test' in msg)
        self.failUnless('From: portal@plone.test' in msg)


class TestModeratorNotificationUnit(PloneTestCase):

    layer = DiscussionLayer

    def afterSetUp(self):
        # Set up a mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

        # We need to fake a valid mail setup
        self.portal.email_from_address = "portal@plone.test"
        self.mailhost = self.portal.MailHost

        # Enable comment moderation
        self.portal.portal_types['Document'].allow_discussion = True
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Discussion Item',),
            ('comment_review_workflow',))

        # Enable moderator notification setting
        registry = queryUtility(IRegistry)
        registry['plone.app.discussion.interfaces.IDiscussionSettings.' +
                'moderator_notification_enabled'] = True

        # Create test content
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Document', 'doc1')
        self.portal_discussion = self.portal.portal_discussion
        # Archetypes content types store data as utf-8 encoded strings
        # The missing u in front of a string is therefor not missing
        self.portal.doc1.title = 'Kölle Alaaf' # What is "Fasching"?
        self.conversation = IConversation(self.portal.doc1)

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)

    def test_notify_moderator(self):
        # Add a comment and make sure an email is send to the moderator.
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        self.conversation.addComment(comment)

        self.assertEquals(len(self.mailhost.messages), 1)
        self.failUnless(self.mailhost.messages[0])
        msg = self.mailhost.messages[0]

        if not isinstance(msg, str):
            # Plone 3
            self.failUnless('portal@plone.test' in msg.mfrom)
            self.failUnless('portal@plone.test' in msg.mto)
        else:
            #Plone 4
            self.failUnless('To: portal@plone.test' in msg)
            self.failUnless('From: portal@plone.test' in msg)

        #We expect the headers to be properly header encoded (7-bit):
        #>>> 'Subject: =?utf-8?q?Some_t=C3=A4st_subject=2E?=' in msg
        #True

        #The output should be encoded in a reasonable manner (in this case
        # quoted-printable):
        #>>> msg
        #'...Another t=C3=A4st message...You are receiving this mail because
        # T=C3=A4st user\ntest@plone.test...is sending feedback about the site
        # you administer at...
    
    def test_notify_moderator_specific_address(self):
        # A moderator email address can be specified in the control panel.
        registry = queryUtility(IRegistry)
        registry['plone.app.discussion.interfaces.IDiscussionSettings' +
                 '.moderator_email'] = 'test@example.com'

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        self.conversation.addComment(comment)
        
        self.assertEquals(len(self.mailhost.messages), 1)
        msg = self.mailhost.messages[0]
        if not isinstance(msg, str):
            self.failUnless('test@example.com' in msg.mto)
        else:
            self.failUnless('To: test@example.com' in msg)

    def test_do_not_notify_moderator_when_no_sender_is_available(self):
        # Set sender mail address to nonw and make sure no email is send to the
        # moderator.
        self.portal.email_from_address = None

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        self.conversation.addComment(comment)
        self.assertEquals(len(self.mailhost.messages), 0)

    def test_do_not_notify_moderator_when_notification_is_disabled(self):
        # Disable moderator notification setting and make sure no email is send
        # to the moderator.
        registry = queryUtility(IRegistry)
        registry['plone.app.discussion.interfaces.IDiscussionSettings.' +
                 'moderator_notification_enabled'] = False

        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        self.conversation.addComment(comment)
        self.assertEquals(len(self.mailhost.messages), 0)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
