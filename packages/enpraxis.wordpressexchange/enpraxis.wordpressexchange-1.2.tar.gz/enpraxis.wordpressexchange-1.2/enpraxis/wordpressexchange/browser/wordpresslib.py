"""
This is a customized version of worpresslib created by
Michele Ferretti <black.bird@tiscali.it>

"""

__author__ = "Jon Thomas <jon@enpraxis.net>"
__version__ = "$Revision: 1.1 $"
__license__ = "LGPL"

import exceptions
import re
import os
import xmlrpclib
import datetime
import time
import string

class WordPressException(exceptions.Exception):
	"""Custom exception for WordPress client operations
	"""
	def __init__(self, obj):
		if isinstance(obj, xmlrpclib.Fault):
			self.id = obj.faultCode
			self.message = obj.faultString
		else:
			self.id = 0
			self.message = obj

	def __str__(self):
		return '%s %d: %s' % (self.__class__.__name__, self.id, self.message)
		
class WordPressBlog:
	"""Represents blog item
	"""	
	def __init__(self):
		self.id = ''
		self.name = ''
		self.url = ''
		self.isAdmin = False
		
class WordPressPage:
	"""Represents page item
	"""	
	def __init__(self):
		self.id = 0
		self.title = ''
		self.date = None
		self.permaLink = ''
		self.description = ''
		self.textMore = ''
		self.link = ''
		self.categories = []
		self.user = ''
		self.allowPings	= False
		self.allowComments = False

		
class WordPressClient:
	"""Client for connect to WordPress XML-RPC interface
	"""
	
	def __init__(self, url, user, password):
		self.url = url
		self.user = user
		self.password = password
		self.blogId = 0
		self.categories = None
		self._server = xmlrpclib.ServerProxy(self.url)


	def selectBlog(self, blogId):
		self.blogId = blogId
		

	def getPage(self, blogId, pageId):
		"""Get Page item
		"""
		try:
			return self._server.wp.getPage(str(blogId), str(pageId), self.user, self.password)
		except xmlrpclib.Fault, fault:
			raise WordPressException(fault)

	def getPageList(self, blogId):
		"""Return Pages List
		"""
		try:
			return self._server.wp.getPageList(str(blogId), self.user, self.password)
		except xmlrpclib.Fault, fault:
			raise WordPressException(fault)
	
	def getUsersBlogs(self):
		"""Get blog's users info
		"""
		try:
			blogs = self._server.blogger.getUsersBlogs('', self.user, self.password)
			for blog in blogs:
				blogObj = WordPressBlog()
				blogObj.id = blog['blogid']
				blogObj.name = blog['blogName']
				blogObj.isAdmin = blog['isAdmin']
				blogObj.url = blog['url']
				yield blogObj
		except xmlrpclib.Fault, fault:
			raise WordPressException(fault)
			
			
	def newMediaObject(self, id, media, mimetype):
		"""Add new media object (image, movie, etc...)
		"""
		try:
			mediaStruct = {
				'type' : mimetype, 
				'name' : id,
				'bits' : xmlrpclib.Binary(media)
			}
			
			result = self._server.metaWeblog.newMediaObject(self.blogId, 
									self.user, self.password, mediaStruct)
			return result['url']
			
		except xmlrpclib.Fault, fault:
			raise WordPressException(fault)
	
	def newPage(self, blogid, title, htmltext, parentid):
		""" Add a new page to the site 
		"""
		try:
			#if author doesn't exist then create a new author on the wordpress blog.
			#Convert the date to a proper date.

			content = {
				'wp_page_parent_id':parentid,
				'title':title,
				'description':htmltext,
				'dateCreated':''
				}

			return self._server.wp.newPage(blogid, self.user, self.password, content, 0)

		except xmlrpclib.Fault, fault:
			raise WordPressException(fault)


