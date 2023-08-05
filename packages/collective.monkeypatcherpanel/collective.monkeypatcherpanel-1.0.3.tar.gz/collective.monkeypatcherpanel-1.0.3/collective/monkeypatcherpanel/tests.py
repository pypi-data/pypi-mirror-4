# -*- coding: utf-8 -*-
# $Id: tests.py 228249 2010-12-05 01:02:42Z glenfant $
"""Testing collective.monkeypatcherpanel"""
import unittest

from Testing import ZopeTestCase
import Products.Five
from Products.Five import zcml
from Products.Five import fiveconfigure

import collective.monkeypatcher
import collective.monkeypatcherpanel

fiveconfigure.debug_mode = True # Don't swallow install exceptions
zcml.load_config('meta.zcml', Products.Five)
zcml.load_config('configure.zcml', Products.Five)
zcml.load_config('configure.zcml', collective.monkeypatcher)
zcml.load_config('configure.zcml', collective.monkeypatcherpanel)
fiveconfigure.debug_mode = False

ZopeTestCase.installPackage('collective.monkeypatcherpanel')

# Some test resources
class DummyClass(object):
    """Blah Blah"""

    def someMethod(self):
        """someMethod docstring"""

        return "original result"

def patchedSomeMethod(self):
    return "patched result"


class MonkeyPatcherPanelTestCase(ZopeTestCase.ZopeTestCase):
    """Base for test cases"""

    def afterSetUp(self):
        # Adding the control panel
        dummy = self.app.unrestrictedTraverse('@@add-monkeypatcherpanel')()
        return

    def test_haveControlPanel(self):
        """Our control panel is installed"""

        cp = self.app.Control_Panel
        self.failUnless('collective_monkeypatcherpanel' in cp.objectIds())
        return

    def test_eventFired(self):
        """Our stupid patch"""

        this_module = __name__
        patch_zcml = """
        <configure
           xmlns="http://namespaces.zope.org/zope"
           xmlns:monkey="http://namespaces.plone.org/monkey"
           i18n_domain="collective.doesntmatter">
           <monkey:patch
              description="What the patch does in short"
              class="%(this_module)s.DummyClass"
              original="someMethod"
              replacement="%(this_module)s.patchedSomeMethod"
              />
        </configure>""" % locals()
        zcml.load_string(patch_zcml)
        all_patches = collective.monkeypatcherpanel.controlpanel.all_patches

        # We got 1 monkey patch
        self.failUnlessEqual(len(all_patches), 1)

        # We got expected patch information
        patch = all_patches[0]
        self.failUnlessEqual(patch['description'], u'What the patch does in short')
        self.failUnlessEqual(patch['original'], '%(this_module)s.DummyClass.someMethod' % locals())
        self.failUnlessEqual(patch['replacement'], '%(this_module)s.patchedSomeMethod' % locals())
        return

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MonkeyPatcherPanelTestCase))
    return suite

