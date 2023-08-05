import unittest2 as unittest
from collective.linguasitemap import testing
from plone.app import testing as ptesting
from plone.browserlayer.layer import mark_layer


class IntegrationTestCase(unittest.TestCase):

    layer = testing.INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        ptesting.setRoles(self.portal, ptesting.TEST_USER_ID, ['Manager'])
        ptesting.login(self.portal, ptesting.TEST_USER_NAME)
        languages = ['en', 'fr', 'nl']
        defaultLanguage = 'en'
        planguages = self.portal.portal_languages
        planguages.manage_setLanguageSettings(defaultLanguage, languages)
        self.portal.invokeFactory('Folder', 'dossier')
        self.folder = self.portal['dossier']
        self.folder.setLanguage('fr')
        self.folder.reindexObject()
        self.portal.portal_properties.site_properties.enable_sitemap = True
        self.request = self.layer['request']
        mark_layer(self.portal, self)


class FunctionalTestCase(IntegrationTestCase):

    layer = testing.FUNCTIONAL

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        #we need to commit to be able to use browser
        import transaction
        transaction.commit()
