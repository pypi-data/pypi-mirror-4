""" Testing
"""
from plone.testing import z2
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer

class MyFixture(PloneSandboxLayer):
    """ EdW User History Policy
    """
    def setUpZope(self, app, configurationContext):
        """ Setup Zope
        """
        import edw.userhistory
        self.loadZCML(package=edw.userhistory)
        z2.installProduct(app, 'edw.userhistory')

    def setUpPloneSite(self, portal):
        """ Setup Plone
        """
        self.applyProfile(portal, 'plone.outputfilters:default')
        self.applyProfile(portal, 'plonetheme.classic:default')
        self.applyProfile(portal, 'edw.userhistory:default')

    def tearDownZope(self, app):
        """ Uninstall Zope
        """
        z2.uninstallProduct(app, 'edw.userhistory')

FIXTURE = MyFixture()
FUNCTIONAL_TESTING = FunctionalTesting(bases=(FIXTURE, ),
                                       name='MyFixture:Functional')
INTEGRATION_TESTING = IntegrationTesting(bases=(FIXTURE, ),
                                         name='MyFixture:Integration')
