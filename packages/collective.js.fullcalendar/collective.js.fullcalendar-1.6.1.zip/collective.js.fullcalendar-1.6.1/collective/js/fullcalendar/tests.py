import unittest

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

ptc.setupPloneSite(products=['collective.js.fullcalendar'])

from Products.CMFCore.utils import getToolByName

import collective.js.fullcalendar


class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.js.fullcalendar)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass
    
    def afterSetUp(self):
        self.js_res_basepath = "++resource++collective.js.fullcalendar/"
        self.css_res_basepath = "++resource++collective.js.fullcalendar/"
        self.js_files = ['fullcalendar.gcal.js',
                         'fullcalendar.min.js',
                         ]
        self.css_files = ['fullcalendar.css',
                          ]

    def test_portal_js(self):
        p_js = getToolByName(self.portal,'portal_javascripts')
        for js_name in self.js_files:
            self.failUnless(self.js_res_basepath + js_name in p_js.getResourceIds(),
                            "%s not found in portal_javascripts" % js_name)
        
    def test_portal_css(self):
        p_css = getToolByName(self.portal,'portal_css')
        for css_name in self.css_files:
            self.failUnless(self.css_res_basepath + css_name in p_css.getResourceIds(),
                            "%s not found in portal_css" % css_name)
        
    def test_js_resources(self):
        for js_name in self.js_files:
            try:
                self.portal.restrictedTraverse(self.js_res_basepath + js_name)
            except AttributeError:
                self.fail('%s resource not found' % js_name)
    

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
