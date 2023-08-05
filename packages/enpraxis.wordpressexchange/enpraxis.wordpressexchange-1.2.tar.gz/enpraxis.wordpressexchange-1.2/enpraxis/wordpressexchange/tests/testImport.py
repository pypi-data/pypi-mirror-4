##################################################################################
#    Copyright (c) 2004-2009 Utah State University, All rights reserved. 
#    Portions copyright 2009 Massachusetts Institute of Technology, All rights reserved.
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation, version 2.                                      
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__  = '''Brent Lambert, David Ray, Jon Thomas'''
__version__   = '$ Revision 0.0 $'[11:-2]

from base import WordpressExchangeTestCase
from enpraxis.wordpressexchange.browser.wpimportform import validate_url
from mocker import Mocker
from plone.mocktestcase import MockTestCase
from Products.CMFPlone.tests.dummy import Dummy
from zope.app.form.interfaces import WidgetInputError

class TestImportForm(WordpressExchangeTestCase):

    def testGetEntryFolderId(self):
        """ Test getting the entry folder id """
        self.loginAsPortalOwner()
        form = self.portal.restrictedTraverse('@@wpimport_form')
        wpid = form._getEntryFolderId()
        self.assertEqual(wpid, 'Imported-WordPress-Pages')
        self.portal.invokeFactory('Folder', 'Imported-WordPress-Pages')
        wpid = form._getEntryFolderId()
        self.assertEqual(wpid, 'Imported-WordPress-Pages-1')
        self.portal.invokeFactory('Folder', 'Imported-WordPress-Pages-1')
        wpid = form._getEntryFolderId()
        self.assertEqual(wpid, 'Imported-WordPress-Pages-2')

    def testValidateUrl(self):
        """ Test the validate url method """
        # create dummy objects to allow method to pass
        dummy = Dummy()
        dummywidget = Dummy()
        dummyerror = Dummy()
        dummycontext = Dummy()
        dummy.validate = lambda x, y: None
        dummycontext.__name__ = 'Dummy Context'
        dummy.context = dummycontext
        dummyerror.label = 'Error'
        dummywidget.get = lambda x: dummyerror
        dummy.widgets = dummywidget
        # Test valid paths
        path1 = validate_url(dummy, None, {'wp_url':'http://www.plone.org'})
        path2 = validate_url(dummy, None, {'wp_url':'https://www.plone.org'})
        path3 = validate_url(dummy, None, {'wp_url':'http://www.plone.org?result=50&start=20'})
        self.assertEqual(path1, None)
        self.assertEqual(path2, None)
        self.assertEqual(path3, None)
        # Test invalid paths verify errors
        path1 = validate_url(dummy, None, {'wp_url':'httpp://www.plone.org'})
        path2 = validate_url(dummy, None, {'wp_url':'gtp://www.plone.org'})
        self.assertEqual('WidgetInputError', path1.__class__.__name__)
        self.assertEqual('WidgetInputError', path2.__class__.__name__)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestImportForm))
    return suite
