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

import wordpresslib
import re

from zope.formlib.form import FormFields, action
from zope.interface import Interface
from zope import schema

from zope.interface import Interface, Attribute
from zope.component import getUtility

from enpraxis.wordpressexchange import WordPressMessageFactory as _

from plone.app.form.base import AddForm
from zope.app.form.browser import PasswordWidget
from zope.formlib.form import FormFields, action, applyChanges
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema import TextLine
from zope.component import getUtility
from zope.publisher.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.app.form.interfaces import WidgetInputError
from urlparse import urlparse
from wordpresslib import WordPressException


from Products.CMFCore.utils import getToolByName
from socket import gaierror
from xmlrpclib import ProtocolError
from BeautifulSoup import BeautifulSoup



def validate_url(form, action, data):
    """ Validate the url. """
    errors = form.validate(action, data)
    if errors:
        return errors
    if data.has_key('wp_url'):
        url = data['wp_url']
        
        expr = re.compile(r'(http)s?://[^\s\r\n]+')
        if not expr.match(url):
            ew = form.widgets.get('wp_url')
            ew._error = WidgetInputError(form.context.__name__, ew.label, _('Invalid url'))
            return ew._error


class IExport(Interface):
    """ Import Form """

    wp_url = TextLine(title=_(u"WordPress URL"),
                           description=_(u"The web address of your WordPress blog."),
                           required=True)

    wp_username = TextLine(title=_(u'User Name'),
                                 description=_(u'Your WordPress user name.'),
                                 required=True)

    wp_password = TextLine(title=_(u'Password'),
                                 description=_(u'Your WordPress password.'),
                                 required=True)

    

class ExportForm(AddForm):
    """ Render the WordPress import form  """
    form_fields = FormFields(IExport)
    form_fields['wp_password'].custom_widget = PasswordWidget

    label = _(u'Export WordPress Pages')
    description = _(u'This form allows you to export documents on your site as WordPress pages. \
                     Enter the information below and click submit. Any documents in this folder \
                     (and in any sub-folders) will be exported to the blog specified.')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.uploaded_images = {}
        self.uploaded_links = {}


    @action(_(u'Submit'), validator=validate_url)
    def action_submit(self, action, data):

        status=IStatusMessage(self.request)
        wp_url = '%s/xmlrpc.php' % self.request.form['form.wp_url']
        wp_user = self.request.form['form.wp_username']
        wp_password = self.request.form['form.wp_password']

        #create WP client object
        wp_client = wordpresslib.WordPressClient(wp_url, wp_user, wp_password)

        brainobjs = self.context.portal_catalog(path={'query':'/'.join(self.context.getPhysicalPath()),'depth':0},)

        try:
            self.exportPage(wp_client, brainobjs[0], 0, '0')
        except (gaierror, ProtocolError):
            status.addStatusMessage(_(u'Unable to establish a connection with that blog'), type='error')
            return self.request.response.redirect('@@wpexport_form')
        except WordPressException, fault:
            if fault.id == 403:
                status.addStatusMessage(_(u'User name and login did not match'), type='error')
            else:
                raise WordPressException(fault)
            return self.request.response.redirect('@@wpexport_form')            


        status.addStatusMessage(_(u'Documents were successfully exported to the WordPress blog.'), type='info')
        return self.request.response.redirect('.')

    
    def exportPage(self, wp_client, brain, blogId, parentid):
        """ Export a page to the WordPress site """
        obj = brain.getObject()
        if obj.isPrincipiaFolderish:

            if getattr(obj, 'getText', None):
                page_text = obj.getText()
                if page_text:
                    soup = self.parseInternalResources(wp_client, page_text)
                    page_text = str(soup)
            else:
                page_text = ''

            gen_parentid = wp_client.newPage(blogId, obj.Title(), page_text, parentid)
            child_objs = brain.portal_catalog.searchResults(path={'query':brain.getPath(),'depth':1},)
        
            for child_obj in child_objs:
                self.exportPage(wp_client, child_obj, blogId, gen_parentid)
                
        else:
            if getattr(obj, 'getText', None):
                page_text = obj.getText()
                if page_text:
                    soup = self.parseInternalResources(wp_client, page_text)
                    page_text = str(soup)
                
                wp_client.newPage(blogId, obj.Title(), page_text, parentid)
                

    def parseInternalResources(self, wp_client, text):
        """ Parse html for internal links to upload to word press  """

        mt = getToolByName(self.context, 'portal_membership') 
        http_host = self.context.REQUEST.HTTP_HOST
        soup = BeautifulSoup(text)
        

        if soup.findAll('img'):
            for img in soup.findAll('img'):
                src = img['src'].encode('ascii')
                
                tp = urlparse(src)
                img_data = ''

                same_host = http_host == tp[1]
                if tp[0] in ('http', 'https', 'ftp') and not same_host:
                    # appears like a remote image, pass, as Word Press will render external images
                    pass
                else:
                    # likely a local image, try to traverse and get hold of the image data
                    # to upload to WordPress
                    img_path = src
                    img_obj =None
                    for path in (img_path, tp[2]):
                        img_obj = self.context.unrestrictedTraverse(path, None)
                        if img_obj:
                            if mt.checkPermission('View', img_obj):
                                try:
                                    img_data = str(img_obj.data)
                                    break
                                except AttributeError:
                                    try:
                                        img_data = str(img_obj._data) # FSImage
                                    except AttributeError:
                                        break
                        else:
                            if self.context.portal_catalog.searchResults(id=path):
                                img_obj = self.context.portal_catalog.searchResults(id=path)[0].getObject()
                                img_data =  img_obj.data

                    if img_data:
                        #Check and see if this image has alredy been uploaded
                        if img_obj.id not in self.uploaded_images.keys():
                            #upload to WordPress, change src location to reflect change
                            mimetype = img_obj.content_type
                            result = wp_client.newMediaObject(img_obj.id, img_data, mimetype)
                            if result:
                                self.uploaded_images[img_obj.id] = result
                                img['src'] = result
                        else:
                            img['src'] = self.uploaded_images[img_obj.id]

        if soup.findAll('a'):
            for link in soup.findAll('a'):
                try:
                    href = link['href'].encode('ascii')
                except KeyError, e:
                    href = ''

                tp = urlparse(href)
                link_data = ''

                same_host = http_host == tp[1]
                if tp[0] in ('http', 'https', 'ftp') and not same_host:
                    # appears like a remote link, pass, as Word Press will render external images
                    pass
                else:
                    # likely a local resource, try to traverse and get hold of the link data
                    # to upload to WordPress
                    link_path = href
                    #ignore links that are named anchors
                    if not link_path.startswith('#') and link_path != '':
                        link_obj =None
                        for path in (link_path, tp[2]):
                            link_obj = self.context.unrestrictedTraverse(path, None)
                            if link_obj and link_obj.Type() == 'File':
                                if mt.checkPermission('View', link_obj):
                                    try:
                                        link_data = str(link_obj.data)
                                        break
                                    except AttributeError:
                                        try:
                                            link_data = str(link_obj._data) # FS Object
                                        except AttributeError:
                                            break
                            else:
                                if self.context.portal_catalog.searchResults(id=path):
                                    link_obj = self.context.portal_catalog.searchResults(id=path)[0].getObject()
                                    if link_obj.Type() == 'File':
                                        link_data = link_obj.data
                    if link_data:
                        #Check to see if this resource has already been uploaded
                        if link_obj.id not in self.uploaded_links.keys():
                            #upload to WordPress, change src location to reflect change
                            mimetype = link_obj.Format()
                            result = wp_client.newMediaObject(link_obj.id, link_data, mimetype)
                            if result:
                                self.uploaded_links[link_obj.id] = result
                                link['href'] = result
                        else:
                            link['href'] = self.uploaded_links[link_obj.id]
        return soup

                

