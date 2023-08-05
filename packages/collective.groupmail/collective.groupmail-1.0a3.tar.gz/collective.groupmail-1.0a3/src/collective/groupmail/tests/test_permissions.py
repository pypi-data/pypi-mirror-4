import base64
import unittest2 as unittest
import transaction
from plone.testing import z2
from plone.app.testing.interfaces import SITE_OWNER_NAME, TEST_USER_ID, TEST_USER_PASSWORD
from Products.CMFCore.utils import getToolByName

from collective.groupmail.testing import COLLECTIVE_GROUPMAIL_FUNCTIONAL_TESTING

class TestPermissions(unittest.TestCase):

    layer = COLLECTIVE_GROUPMAIL_FUNCTIONAL_TESTING
    
    def browser(self, login=None, password=None):
        """Browser of authenticated user
        """
        browser = z2.Browser(self.layer['app'])
        browser.handleErrors = False
        
        if login is None or password is None:
            return browser

        browser.open(self.layer['portal'].absolute_url() + '/login_form')
        browser.getControl(name='__ac_name').value = login
        browser.getControl(name='__ac_password').value = password
        browser.getControl(name='submit').click()

        return browser
    
    
    def setUp(self):
        portal = self.layer['portal']
        app = self.layer['app']

        # Setup the mailaddress
        portal.email_from_address = 'foo@frotz.bar'
        portal.email_from_name = 'Admin'

        # Create users and groups
        acl_users = getToolByName(portal, 'acl_users')
        group_tool = getToolByName(portal, 'portal_groups')
        registration = getToolByName(portal, 'portal_registration')

        # Ordinary user, can list users and groups, send personal emails but not send group emails
        registration.addMember('ordinary', 'secret', 
                               properties={
                                   'username': 'ordinary',
                                   'fullname': 'Ordinary',
                                   'email': 'ordinary@foo.bar'
                               })

        # Ordinary user, can list users and groups, send personal emails but not send group emails
        registration.addMember('listing', 'secret', 
                               properties={
                                   'username': 'listing',
                                   'fullname': 'Listing',
                                   'email': 'listing@foo.bar'
                               })

        # User that can send group mails
        registration.addMember('privileged', 'secret', 
                               properties={
                                   'username': 'privileged',
                                   'fullname': 'Privileged',
                                   'email': 'privileged@foo.bar'
                               })

        # Group for those that can list users and send them mails
        group_tool.addGroup('userlisters', [], [], title="User listers group")
        group_tool.addPrincipalToGroup('privileged', 'userlisters')

        # Group for those that can list groups
        group_tool.addGroup('grouplisters', [], [], title="Group listers group")
        group_tool.addPrincipalToGroup('privileged', 'grouplisters')

        # Group for those that can send group mails
        group_tool.addGroup('mailsenders', [], [], title="Mailsenders group")
        group_tool.addPrincipalToGroup('privileged', 'mailsenders')
        
        # Group to send emails to
        group_tool.addGroup('testgroup', [], [], title="Test group")
        group_tool.addPrincipalToGroup('privileged', 'testgroup')
        group_tool.addPrincipalToGroup('ordinary', 'testgroup')
        group_tool.addPrincipalToGroup('listing', 'testgroup')

        transaction.commit()

    def test_anonymous(self):
        portal = self.layer['portal']
        portal_url = portal.absolute_url()
        browser = self.browser()

        # Open User page
        browser.open(portal_url + '/Members')
        
        # Search for a group, lowercase partial should work:
        browser.getControl(name='fullname').value = 'test'
        browser.getControl(name='submit').click()
        
        self.assertTrue('You are not allowed to list portal members.' in browser.contents)

    def test_ordinary_user(self):
        portal = self.layer['portal']
        portal_url = portal.absolute_url()
        browser = self.browser('ordinary', 'secret')

        # Open User page
        browser.open(portal_url + '/Members')
        
        # Search for a group, lowercase partial should work:
        browser.getControl(name='fullname').value = 'Test'
        browser.getControl(name='submit').click()
        
        # Check that we found the group, the whole group and nothing but the group:
        self.assertTrue('Test group' in browser.contents)
        self.assertTrue('Administrators' not in browser.contents)
        
        browser.getLink('Test group').click()

        browser.getControl('Subject').value = 'Email to group'
        browser.getControl('Message').value = 'This is the message:\nHello!\n'
        browser.getControl('Send').click()
        
        self.assertTrue('Mail sent to listing@foo.bar,ordinary@foo.bar,privileged@foo.bar' in browser.contents)
        self.assertEqual(len(portal.MailHost.messages), 3)

    #def test_privileged_user(self):
        #portal = self.layer['portal']
        #portal_url = portal.absolute_url()
        #browser = self.browser('ordinary', 'secret')

        ## Open User page
        #browser.open(portal_url + '/Members')
        
        ## Search for a group, lowercase partial should work:
        #browser.getControl(name='fullname').value = 'Test'
        #browser.getControl(name='submit').click()
        
        ## Check that we found the group, the whole group and nothing but the group:
        #self.assertTrue('Test group' in browser.contents)
        #self.assertTrue('Administrators' not in browser.contents)
        
        #browser.getLink('Test group').click()

        #browser.getControl('Subject').value = 'Email to group'
        #browser.getControl('Message').value = 'This is the message:\nHello!\n'
        #browser.getControl('Send').click()
        
        #self.assertTrue('Mail sent to listing@foo.bar,ordinary@foo.bar,privileged@foo.bar' in browser.contents)
        #self.assertEqual(len(portal.MailHost.messages), 3)
