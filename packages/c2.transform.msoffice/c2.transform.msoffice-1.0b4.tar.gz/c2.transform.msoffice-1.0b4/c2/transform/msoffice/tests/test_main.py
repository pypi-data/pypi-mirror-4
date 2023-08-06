import unittest

import os
import StringIO
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.MimetypesRegistry.interfaces import IMimetype

from c2.transform.msoffice.config import TRANSFORM_NAME
from c2.transform.msoffice.config import office_mimetypes

ptc.setupPloneSite()

import c2.transform.msoffice

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             c2.transform.msoffice)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

class PTTestCase(TestCase):
    """Testing portal_transforms settings"""

    def afterSetUp(self):
        qi = self.portal.portal_quickinstaller
        qi.installProduct('c2.transform.msoffice')
        qi.installProduct('collective.indexing')

        portal = self.getPortal()
        self.pt = getToolByName(portal, 'portal_transforms')


    def testInstallation(self):
        """Checking installation of our transform"""

        self.failUnless(TRANSFORM_NAME in self.pt.objectIds(spec='Transform'),
                        "%s transform expected" % TRANSFORM_NAME)
        return


    def testATfileSearchableText(self):
        """Do we index the text of an openxml office file"""

        self.loginAsPortalOwner()
        class fakefile(StringIO.StringIO):
            pass
        this_dir = os.path.dirname(os.path.abspath(__file__))
        test_filename = os.path.join(this_dir, 'wordprocessing1.docx')
        fakefile = fakefile(file(test_filename, 'rb').read())
        fakefile.filename = 'wordprocessing1.docx'
        file_id = self.portal.invokeFactory('File', fakefile.filename, file=fakefile)
        file_item = getattr(self.portal, file_id)
        # We sample some words from the file and its metadata
        words = ("a", "simple", "example", "of", "document", "with",
                 "full", "set", "metadata", "comments")
        st = file_item.SearchableText()
        for word in words:
            self.failUnless(word in st, "Expected '%s' in indexable text" % word)
        return


class MTRTestCase(TestCase):

    def afterSetUp(self):
        portal = self.getPortal()
        self.mtr = getToolByName(portal, 'mimetypes_registry')


    def testInstallation(self):
        """Checking installation of our Mime types"""
        providedBy = getattr(IMimetype, 'providedBy', 
                        getattr(IMimetype, 'isImplementedBy', None))
        mtr = self.mtr
        for mt_dict in office_mimetypes:
            mt_string = mt_dict['mimetypes'][0]
            mimetype = mtr.lookup(mt_string)
            self.failUnless(
                len(mimetype) > 0,
                "Didn't find MimeType obj for %s" % mt_string)
            if len(mimetype) > 0:
                self.failUnless(
                    providedBy(mtr.lookup(mt_string)[0]),
                    "Didn't find MimeType obj for %s" % mt_string)
        return


    def testExtensions(self):
        """Finding mimetypes by extension"""

        mtr = self.mtr
        for mt_dict in office_mimetypes:
            ext = mt_dict['extensions'][0]
            expected = mt_dict['mimetypes'][0]
            got = mtr.lookupExtension(ext).normalized()
            self.failUnlessEqual(expected, got)
        return



def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(PTTestCase),
        unittest.makeSuite(MTRTestCase),

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='c2.transform.msoffice',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='c2.transform.msoffice.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='c2.transform.msoffice',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='c2.transform.msoffice',
        #    test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
