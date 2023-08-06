import urllib2

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from zope.configuration import xmlconfig
from openmultimedia.headband.config import PROJECTNAME


def generate_jpeg_file(width, height):
    url = 'http://lorempixel.com/%d/%d/' % (width, height)
    return urllib2.urlopen(url)


def generate_jpeg(width, height):
    return generate_jpeg_file(width, height).read()


class OpenmultimediaheadbandLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import openmultimedia.headband
        xmlconfig.file('configure.zcml',
                       openmultimedia.headband,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, '%s:default' % PROJECTNAME)
        applyProfile(portal, '%s:testing' % PROJECTNAME)


OPENMULTIMEDIA_HEADBAND_FIXTURE = OpenmultimediaheadbandLayer()
OPENMULTIMEDIA_HEADBAND_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OPENMULTIMEDIA_HEADBAND_FIXTURE,),
    name="OpenmultimediaheadbandLayer:Integration")
OPENMULTIMEDIA_HEADBAND_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENMULTIMEDIA_HEADBAND_FIXTURE, ),
    name="OpenmultimediaheadbandLayer:Functional")
