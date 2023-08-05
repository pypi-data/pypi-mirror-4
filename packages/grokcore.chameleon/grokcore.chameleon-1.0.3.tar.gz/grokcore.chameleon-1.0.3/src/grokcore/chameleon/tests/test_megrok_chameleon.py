"""Test setup for grokcore.chameleon.
"""
import doctest
import unittest
import zope.interface
import zope.component
import grokcore.chameleon

from zope.traversing.interfaces import ITraversable
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.publisher.interfaces.browser import IBrowserRequest
from grokcore.chameleon.tests import FunctionalLayer

FLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

class DummyResource(object):
    """ Dummy resource implementation. """
    zope.interface.implements(ITraversable, IAbsoluteURL)

    def __init__(self, request, name=''):
        self.request = request
        self.name = name

    def traverse(self, name, furtherPath):
        name = '%s/%s' % (self.name, name)
        return DummyResource(self.request, name=name)

    def __str__(self):
        return 'dummy:%s' % self.name

def setUpStatic(test):
    # Register a dummy resource for static folder.
    zope.component.provideAdapter(
        factory=DummyResource,
        adapts=(IBrowserRequest,),
        provides=zope.interface.Interface,
        name='grokcore.chameleon.tests.cpt_fixture'
        )
    return


def test_suite():
    """Get a testsuite of all doctests.
    """
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        'README.txt',
        setUp=setUpStatic,
        package=grokcore.chameleon,
        globs=dict(
            getRootFolder=FunctionalLayer.getRootFolder,
            ),
        optionflags=FLAGS,
        )
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    suite.addTest(
        doctest.DocTestSuite(
            'grokcore.chameleon.tests.templatefile',
            setUp=setUpStatic,
            optionflags=FLAGS,
            )
        )
    return suite
