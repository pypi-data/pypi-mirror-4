import unittest

#from zope.testing import doctestunit
#from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import fiveconfigure, zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from zope.interface.declarations import alsoProvides
ptc.setupPloneSite()

import collective.local.userlisting
from collective.local.userlisting.interfaces import IUserListingAvailable


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(collective.local.userlisting)
            zcml.load_config('configure.zcml',
                             collective.local.userlisting)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


USERDEFS = [
        {'user': 'manager', 'roles': ('Member', 'Manager'), 'groups': ()},
        {'user': 'siteadmin', 'roles': ('Member'), 'groups': ()},
        {'user': 'member', 'roles': ('Member',), 'groups': ()},
        {'user': 'reader', 'roles': ('Member',), 'groups': ()},
        {'user': 'reader2', 'roles': ('Member',), 'groups': ()},
        {'user': 'contributor', 'roles': ('Member',), 'groups': ()},
        {'user': 'editor', 'roles': ('Member',), 'groups': ()},
        {'user': 'reviewer', 'roles': ('Member',), 'groups': ()},
        ]


def createMembers(portal):
    pas = portal.acl_users
    gtool = portal.portal_groups
    for userinfo in USERDEFS:
        username = userinfo['user']
        pas.userFolderAddUser(username, 'secret', userinfo['roles'], [])


class UserListingTest(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        portal = self.portal
        createMembers(portal)

        portal.portal_membership.getMemberById('reader2'
                            ).setMemberProperties({'listed': False})

        portal.portal_membership.getMemberById('editor'
                            ).setMemberProperties({'listed': False})

        portal.invokeFactory('Folder', 'folder1')
        portal.invokeFactory('Folder', 'folder2')
        alsoProvides(portal.folder1, IUserListingAvailable)

        portal.folder1.manage_addLocalRoles('reader', ('Reader',))
        portal.folder1.manage_addLocalRoles('reader2', ('Reader',))
        portal.folder1.manage_addLocalRoles('contributor', ('Contributor',))
        portal.folder1.manage_addLocalRoles('reviewer', ('Reviewer',))
        portal.folder1.manage_addLocalRoles('editor', ('Editor',))
        portal.folder1.manage_addLocalRoles('member', ('Member',))

    def test_userlisting(self):
        self.loginAsPortalOwner()
        folder1 = self.portal.folder1
        folder2 = self.portal.folder2
        self.failUnless(folder1.restrictedTraverse('@@userlistingavailable')())
        self.failIf(folder2.restrictedTraverse('@@userlistingavailable')())

        users_by_role = folder1.restrictedTraverse('@@userlisting').users_by_role()

        self.assertEqual(len(users_by_role), 3)
        self.assertEqual(users_by_role[0]['users'][0]['id'], 'reviewer')
        self.assertEqual(users_by_role[1]['users'][0]['id'], 'contributor')
        self.assertEqual(len(users_by_role[2]['users']), 1)
        self.assertEqual(users_by_role[2]['users'][0]['id'], 'reader')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(UserListingTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
