"""Flickr API.

Public class:		FlickrAgent
Public functions:	convertDate
					photoURL
"""
# Author: Eitan Isaacson <eitan@ascender.com> November 2005.
# Maintained by: Bret Walker
# 
# Copyright 2005 Eitan Isaacson <eitan@ascender.com>
# Copyright 2007 Bret Walker
#
# This library is free software; you can redistribute it and/or modify it under 
# the terms of the GNU Lesser General Public License as published by the Free 
# Software Foundation; either version 2.1 of the License, or (at your option) 
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more 
# details.
#
# You should have received a copy of the GNU Lesser General Public License 
# along with this library; if not, write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

__version__ = "0.5"
__all__ = ['FlickrAgent', 'convertDate', 'photoURL']

import xml.dom.minidom, md5, os, httplib, time
from xmlrpclib import ServerProxy
	
_host='www.flickr.com'
_rpc_path='/services/xmlrpc/'
_upload_path='/services/upload/'
_auth_path='/services/auth/'

class FlickrAgent:
	'''FlickrAgent():
	api_key: (required)
	shared_secret: (required)
	token: A valid token
	user: The token's owner
	rcdir: Directory where the tokens are stored automatically by saveToken()
			(default: ~/.flickrlib/)
	rcfile: File name for token storage (default: API key)
	
	If no token or username is provided FlickrAgent will try to load one from disk.
	If this fails the FlickrAgent instance is not authenticated'''
	def __init__(self, api_key,ssecret,token=None,user=None,rcdir='~/.flickrlib/',rcfile=None):
		self.api_key = api_key
		self.ssecret = ssecret
		self._rcdir = os.path.expanduser(rcdir)
		self._rcfile = rcfile or self.api_key
		if not token or user:
			self._token,self._user = self.loadToken()
		else:
			self._token,self._user = token,user
		self._serverProxy = ServerProxy('http://'+_host+_rpc_path)
	def _createSig(self,kwargs):
		str_sig = []
		for key in kwargs.keys():
			str_sig.append('%s%s' % (key, kwargs[key]))
		str_sig.sort()
		return md5.new(self.ssecret + ''.join(str_sig)).hexdigest()
	def authLoginURL(self,perms):
		'''Issues a frob and returns a URL for the user to authorize a program
		perms: read, write, delete'''
		base = 'http://'+_host+_auth_path		
		kwargs = {}
		kwargs['api_key'] = self.api_key
		kwargs['perms'] = perms
		self.frob = kwargs['frob'] = self.flickr.auth.getFrob()['text']
		api_sig = self._createSig(kwargs)
		str_arg = []
		for key in kwargs.keys():
			str_arg.append('%s=%s' % (key, kwargs[key]))
		str_arg.append('api_sig=%s' % api_sig)
		return base+'?'+'&'.join(str_arg)
	def retrieveToken(self):
		'''Retrieves a token after a user authorizes a program via the Flickr website.
		The token is automatically applied to the running instance of FlickrAgent'''
		reply =  self.flickr.auth.getToken(frob=self.frob)
		self._user = user = reply['user'][0]['username']
		self._token = reply['token'][0]['text']
	def saveToken(self):
		'''Saves the token in the running instance to disk'''
		if not self._user or not self._token:
			raise StandardError, 'No token or username in this instance'
		if not os.path.exists(self._rcdir):
			os.makedirs(self._rcdir)
		f = file(os.path.join(self._rcdir, self._rcfile), 'w')
		f.write('token='+self._token+'\n')
		f.write('user='+self._user+'\n')
		f.close()
	def loadToken(self):
		'''Loads a token from disk to the running instance'''
		try:
			f = file(os.path.join(self._rcdir, self._rcfile))
			values = dict([s.strip().split('=') for s in f.readlines()])
			f.close()
			return values['token'], values['user']
		except:
			return None,None
	def parseData(self, xmlStr):
		'''Parses an XML string in to a nested dictionary'''
		if xmlStr.strip() is '':
			return
		dom = xml.dom.minidom.parseString(xmlStr.strip().encode("utf-8"))
		return self.__parseRecursively(dom.firstChild)
	def __parseRecursively(self,element):
		flickrDict = {}
		flickrDict[u'type'] = element.nodeName
		flickrDict[u'text'] = ''
		for attrib in element.attributes.values():
			flickrDict[attrib.nodeName] = attrib.nodeValue
		for node in element.childNodes:
			if node.nodeType == xml.dom.Node.TEXT_NODE:
				flickrDict[u'text'] += node.nodeValue.strip()
			elif node.nodeType == xml.dom.Node.ELEMENT_NODE:
				try:
					flickrDict[node.nodeName].append(self.__parseRecursively(node))
				except KeyError:
					flickrDict[node.nodeName] = [self.__parseRecursively(node)]
				except AttributeError:
					flickrDict[node.nodeName] = [flickrDict[node.nodeName],
												 self.__parseRecursively(node)]
		return flickrDict
	def __call__(self,**kwargs):
		return FlickrAgent.__dict__['_stop'](self,self.n,self.pid,**kwargs)   
	def __getattr__(self,name):
		if name in ('__str__','__repr__'): return lambda:'instance of %s at %s' % (str(self.__class__),id(self))
		if not self.__dict__.has_key('n'):
			self.n=[]
			self.pid = []
		self.n.append(name)
		self.pid.append(str(os.getpid()))
		return self
	def _stop(self,n,pid,**kwargs):
		self.n=[]
		self.pid=[]
		return self._rpc_call(n,pid,**kwargs)
	def _rpc_call(self,n,pid,**kwargs):
		if '.'.join(n) == 'flickr.photos.upload':
			return self.parseData(self._upload(kwargs))
		kwargs['api_key'] = self.api_key
		if self._token:
			kwargs['auth_token'] = self._token				
		kwargs['api_sig'] = self._createSig(kwargs)
		return self.parseData(getattr(self._serverProxy, '.'.join(n))(kwargs))
	def _upload(self,kwargs):
		if not kwargs.get('filename'):
			raise ValueError, 'Must provide a file name'
		filename = kwargs.pop('filename')
		if kwargs.get('title'):
			title = kwargs.pop('title')
		else:
			title = filename
		kwargs['api_key'] = self.api_key
		kwargs['auth_token'] = self._token
		kwargs['api_sig'] = self._createSig(kwargs)
		boundary = '--===Have=a=nice=day=========7d45e178b0434\r\nContent-Disposition: form-data; '
		headers = {"Content-Type": "multipart/form-data; boundary=%s" % boundary[2:-34],
				   "Host": "www.flickr.com"}
		body = ''
		for key in kwargs.keys():
			body += '%sname=%s\r\n\r\n%s\r\n' % (boundary,key,kwargs[key])
		body += '%sname="photo"; filename="%s"\r\n' % (boundary, title)
		body += 'Content-Type: image/jpeg\r\n\r\n'

		f = file(filename, 'rb')
		image = f.read()
		f.close()
		post_data = body.encode("utf_8") + image + ("--%s--" % (boundary[:34])).encode("utf_8")
		conn = httplib.HTTPConnection(_host)
		conn.request("POST", _upload_path, post_data, headers)
		response = conn.getresponse().read()		
		conn.close()
		return response



def convertDate(date_str):
	"""Convert a Flickr formated date to epoch"""
	return time.mktime(
		map(int,
	    	date_str.split(' ')[0].split('-') +
	    	date_str.split(' ')[1].split(':') +
	    	[0,0,0]))

def photoURL(photo,size=None,format='jpg'):
	'''Return a URL for a photo.
	photo: dictionary {'server': <server>, 'id': <id>, 'secret': <secret>}
	size: s=square t=thumbnail m=small b=large o=original
	format: jpg (default), png, gif'''
	if not size:
		return 'http://static.flickr.com/%s/%s_%s.%s' % (photo['server'],photo['id'],photo['secret'],format)
	else:
		return 'http://static.flickr.com/%s/%s_%s_%s.%s' % (photo['server'],photo['id'],photo['secret'],size,format)

