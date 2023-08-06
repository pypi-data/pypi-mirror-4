# -*- coding: utf-8 -*-

from zope.configuration import xmlconfig

from plone.testing import z2

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_NAME, TEST_USER_ID
from plone.app.testing import login


class ATMigrator(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import rt.atmigrator
        xmlconfig.file('configure.zcml',
                       rt.atmigrator,
                       context=configurationContext)
        # z2.installProduct(app, 'rer.sitesearch')

    def setUpPloneSite(self, portal):
        # applyProfile(portal, 'rer.sitesearch:default')
        setRoles(portal, TEST_USER_ID, ['Member', 'Manager'])
        portal.invokeFactory('Folder',
                             'folder-1',
                             title="Folder 1")
        portal.invokeFactory('Folder',
                             'folder-2',
                             title="Folder 2",
                             description="A folder description")

        for i in range(0, 10):
            """
            create some documents
            """
            portal.invokeFactory('Document',
                                 'my-page-' + str(i),
                                 title="My page " + str(i),
                                 text='spam spam')
        for i in range(0, 5):
            """
            create some news
            """
            portal.invokeFactory('News Item',
                                 'my-news-' + str(i),
                                 title="My news " + str(i),
                                 text='spam chocolate ham eggs')

ATMIGRATOR_FIXTURE = ATMigrator()

ATMIGRATOR_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(ATMIGRATOR_FIXTURE, ),
                       name="ATMigrator:Integration")
ATMIGRATOR_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(ATMIGRATOR_FIXTURE, ),
                       name="ATMigrator:Functional")
