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

import os
import re
import urllib2
import wordpresslib

from zope.formlib.form import FormFields, action
from zope import schema

from zope.interface import Interface, Attribute
from enpraxis.wordpressexchange import WordPressMessageFactory as _
from plone.app.form.base import AddForm
from zope.app.form.browser import PasswordWidget
from zope.formlib.form import FormFields, action, applyChanges
from zope.interface import Interface

from zope.schema import TextLine
from Products.statusmessages.interfaces import IStatusMessage
from zope.app.form.interfaces import WidgetInputError
from Products.CMFCore.utils import getToolByName
from enpraxis.wordpressexchange.config import VALID_ID_LIMIT
from enpraxis.wordpressexchange.config import FOLDER_ID_STRING
from urlparse import urlparse
from wordpresslib import WordPressException
from zope.component import getMultiAdapter
from urlparse import urlparse

from socket import gaierror
from xmlrpclib import ProtocolError
from BeautifulSoup import BeautifulSoup
from Products.validation import validation
 

def validate_url(form, action, data):
    """ Validate the url. """
    errors = form.validate(action, data)
    if errors:
        return errors
    if data.has_key('wp_url'):
        url = data['wp_url']
        urlvalidator = validation.validatorFor('isURL')
        if urlvalidator(url.encode('utf-8')) != 1:
            ew = form.widgets.get('wp_url')
            return WidgetInputError(form.context.__name__, ew.label, _(u'Invalid url'))


class IImport(Interface):
    """ Import Form """

    wp_url = TextLine(title=_(u"WordPress URL"),
                           description=_(u"The base url of your WordPress Blog."),
                           required=True)

    wp_username = TextLine(title=_(u'User Name'),
                                 description=_(u'Your WordPress user name'),
                                 required=True)

    wp_password = TextLine(title=_(u'Password'),
                                 description=_(u'Your WordPress password'),
                                 required=True)


class ImportForm(AddForm):
    """ Render the WordPress import form  """
    form_fields = FormFields(IImport)
    form_fields['wp_password'].custom_widget = PasswordWidget

    label = _(u'Import WordPress Pages')
    description = _(u'This form allows you to import WordPress pages. WordPress pages typically contain contact information, licensing information, and other general information. Blog posts and comments are not WordPress pages. This form imports WordPress pages, while maintaining the same hierarchical structure. Enter the information below and press the submit button to retrieve pages from the specified WordPress blog. ')

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.pagedictionary = {} 
        self.parentids = []
        self.wp_client = None
        self.blogId = 0


    @action(_(u'Submit'), validator=validate_url, name=u'Submit')
    def action_submit(self, action, data):

        status=IStatusMessage(self.request)

        if self.request.form['form.wp_url'][-1] == '/':
            wp_url = '%s/xmlrpc.php' % self.request.form['form.wp_url'][:-1]
            blog_url = self.request.form['form.wp_url'][:-1]
        else:
            wp_url = '%s/xmlrpc.php' % self.request.form['form.wp_url']
            blog_url = self.request.form['form.wp_url']

        wp_user = self.request.form['form.wp_username']
        wp_password = self.request.form['form.wp_password']

        #create WP client object
        self.wp_client = wordpresslib.WordPressClient(wp_url, wp_user, wp_password)
        self.blogId = self.wp_client.selectBlog(0)

        wpfolderid = self._getEntryFolderId()

        # Get Pages
        try:
            pages = self.wp_client.getPageList(self.blogId)
        except (gaierror, ProtocolError):
            status.addStatusMessage(_(u'Unable to establish a connection with that blog'), type='error')
            return self.request.response.redirect('@@wpimport_form')
        except WordPressException, fault:
            if fault.id == 403:
                status.addStatusMessage(_(u'User name and login did not match'), type='error')
            else:
                raise WordPressException(fault)
            url = getMultiAdapter((self.context, self.request), name='absolute_url')()
            self.request.response.redirect('%s/@@wpimport_form' %(url))
            return ''

        # Check for at least one published page
        published = False
        for page in pages:
            page_id = page['page_id']
            page_info = self.wp_client.getPage(self.blogId, page_id)
            
            if page_info['page_status'] != 'publish':
                published = False
            else:
                published = True
                break

        if published == False:
            status.addStatusMessage(_(u'Found no published pages to import'), type='error')
            return self.request.response.redirect('@@wpimport_form')
                
        # Create the main folder
        self.context.invokeFactory('Folder', id=wpfolderid)
        wpfolder = getattr(self.context, wpfolderid)

        #Create list of parent items               
        for page in pages:
            if page['page_parent_id'] not in self.parentids:
                self.parentids.append(page['page_parent_id'])

        for page in pages:
            self.importObject(page, wpfolder, blog_url)

        status.addStatusMessage(_(u'Pages imported successfully.'), type='info')
        return self.request.response.redirect('.')

    def importObject(self, page, wpobj, blog_url):

        page_id = page['page_id']
        parent_page_id = page['page_parent_id']
        page_info = self.wp_client.getPage(self.blogId, page_id)

        if page_info['page_status'] != 'publish':
            return None

        # if already created return the object
        fo_obj = self.context.portal_catalog(path={'query':'/'.join(wpobj.getPhysicalPath())}, id=page_id)
        if fo_obj:
            return fo_obj[0].getObject()

        # find the parent
        if parent_page_id == '0':
            parent = wpobj
        else:
            fo_parent = self.context.portal_catalog(path={'query':'/'.join(wpobj.getPhysicalPath())}, id=parent_page_id)        
            if fo_parent:
                parent = fo_parent[0].getObject()
            else:
                parent = self.importObject(parent_page_id, wpobj)

        # in parent is not published don't create children
        if not parent:
            return None
                
        # get page info
        title = page_info['title']

        text = page_info['description']
        #convert line breaks 
        if text:
            text = text.replace('\n', '<br />')

        categories = page_info['categories']
        if 'Uncategorized' in categories:
            categories.remove('Uncategorized')
        state = page_info['page_status']

        # when the page contains other pages then add it as a folder
        if page_id in self.parentids:            

            parent.invokeFactory('Folder', page_id)
            newobj = getattr(parent, page_id)
            newobj.setTitle(title)

            newobj.invokeFactory('Document', 'index_html')
            indexobj = getattr(newobj, 'index_html')
            indexobj.setTitle(title)

            #import files/images/etc from blog to plone
            soup = self.importPageResources(blog_url, text, wpobj)
            text = str(soup)

            indexobj.setText(text, mimetype='text/html')
            if categories != None:
                indexobj.setSubject(categories)

            indexobj.reindexObject()
            newobj.setDefaultPage('index_html')

        else:
            parent.invokeFactory('Document',page_id)
            newobj = getattr(parent, page_id)
            newobj.setTitle(title)

            #import files/images/etc from blog to plone
            soup = self.importPageResources(blog_url, text, wpobj)
            text = str(soup)

            newobj.setText(text, mimetype='text/html')
            if categories != None:
                newobj.setSubject(categories)

        newobj.reindexObject()
        return newobj


    def _getEntryFolderId(self):

        pfid = wpid = FOLDER_ID_STRING

        i = 1
        while i < VALID_ID_LIMIT:
            if wpid in self.context.objectIds():
                wpid = '%s-%s' %(pfid, i)
                i += 1
            else:
                break
        else:
            raise WordPressException(_(u'Exceeded number of rename attempts.'))

        return wpid

    def importPageResources(self, blog_url, text,  wp_obj):
        """ Parses text for resources in the page that are hosted by the WP blog and imports them into the ZODB  """

        mt = getToolByName(self.context, 'portal_membership') 
        http_host = urlparse(blog_url)[1]
        soup = BeautifulSoup(text)
        
        if soup.findAll('img'):
            for img in soup.findAll('img'):
                src = img['src'].encode('ascii')
                
                tp = urlparse(src)
                img_data = ''

                same_host = http_host == tp[1]
                # Check for WordPress 2.7.1 which places a files entry within url
                if not same_host and len(http_host.split('.')) > 1:
                    wp0 = http_host.split('.')[0]
                    wp1 = '.'.join(http_host.split('.')[1:])
                    same_host = '%s.%s.%s' %(wp0, 'files', wp1) == tp[1]

                if tp[0] in ('http', 'https', 'ftp') and not same_host:
                    # appears like a remote image, pass, as Plone will render external images
                    pass
                else:
                    # likely a WP image, try to traverse and get hold of the image data
                    # to upload to the ZODB
                    img_path = src

                    try:
                        img_data = urllib2.urlopen(img_path).read()
                    except Exception, e:
                        break

                    if img_data:
                        #Create resources folder in root of import
                        if not hasattr(wp_obj, 'imported-resources'):
                            wp_obj.invokeFactory('Folder', 'imported-resources')
                            resources = getattr(wp_obj, 'imported-resources')
                            resources.setTitle('Imported Resources')
                            resources.reindexObject()

                        #Create Image in ZODB
                        resources = getattr(wp_obj, 'imported-resources')
                        img_name = os.path.basename(img_path)
                        if not hasattr(resources, img_name):
                            resources.invokeFactory('Image', id=img_name, title=img_name, image=img_data)
                        obj = getattr(resources, img_name)
                        obj.reindexObject()

                        img['src'] = obj.absolute_url()
                        
        if soup.findAll('a'):
            for link in soup.findAll('a'):
                href = link['href'].encode('ascii')

                tp = urlparse(href)
                link_data = ''

                same_host = http_host == tp[1]
                if tp[0] in ('http', 'https', 'ftp') and not same_host:
                    # appears like a remote link, pass, as Word Press will render external images
                    pass
                else:
                    # likely a WP file, try to traverse and get hold of the file data
                    # to upload to the ZODB
                    link_path = href

                    try:
                        link_data = urllib2.urlopen(link_path).read()
                    except Exception, e:
                        break
                                                                

                    if link_data:
                        #Create resources folder in root of import
                        if not hasattr(wp_obj, 'imported-resources'):
                            wp_obj.invokeFactory('Folder', 'imported-resources')
                            resources = getattr(wp_obj, 'imported-resources')
                            resources.setTitle('Imported Resources')
                            resources.reindexObject()

                        #Create File in ZODB
                        resources = getattr(wp_obj, 'imported-resources')
                        file_name = os.path.basename(link_path)
                        if not hasattr(resources, file_name):
                            resources.invokeFactory('File', id=file_name, title=file_name, file=link_data)
                        obj = getattr(resources, file_name)
                        obj.reindexObject()

                        link['href'] = obj.absolute_url()

        return soup
