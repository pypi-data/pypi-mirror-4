import os
import unittest2 as unittest
import doctest
import pprint
from interlude import interact
from plone.testing import (
    layered,
    z2,
)

from openmultimedia.headband.testing import OPENMULTIMEDIA_HEADBAND_FUNCTIONAL_TESTING


TESTFILES = [
    ('../docs/configlet.rst', OPENMULTIMEDIA_HEADBAND_FUNCTIONAL_TESTING),
    ('../docs/viewlet.rst', OPENMULTIMEDIA_HEADBAND_FUNCTIONAL_TESTING),
]

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
optionflags |= doctest.REPORT_ONLY_FIRST_FAILURE

test_home = os.path.dirname(__file__)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([layered(doctest.DocFileSuite(docfile,
                                                 globs={'interact': interact,
                                                        'pprint':
                                                        pprint.pprint,
                                                        'z2': z2,
                                                        'test_home': test_home,
                                                        },
                                                 optionflags=optionflags,
                                                 ),
                            layer=layer,
                            ) for docfile, layer in TESTFILES])
    return suite
