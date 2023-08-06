# -*- coding: utf-8 -*-
from jinja2 import Template
from os.path import dirname,normpath,join,exists,abspath
import re,cgi,sys,imp,os,gzip,tempfile
from time import gmtime,strftime
from wsgiref.util import request_uri
from pysite.tools.log import logger,get_traceback
from pysite.localization import localization
from pysite.conf import getConfiguration
import httpheader

#Last-Modified: Thu, 13 Dec 2012 13:13:59 GMT
#Accept-Ranges: bytes
#Vary: Accept-Encoding
#Content-Encoding: gzip
#Content-Length: 2106
#Content-Type: application/javascript


#Last-Modified: Thu, 13 Dec 2012 13:13:57 GMT
#Accept-Ranges: bytes
#Vary: Accept-Encoding
#Content-Encoding: gzip
#Content-Length: 263
#Content-Type: text/css


#Last-Modified: Thu, 13 Dec 2012 13:13:57 GMT
#Accept-Ranges: bytes
#Content-Length: 1722
#Content-Type: image/png



ext_map_content_type = {
	'js': {
		'Content-Type': 'application/javascript',
		'Content-Encoding': 'gzip'
	},
	'html': {
		'Content-Type': 'text/html',
		'Content-Encoding': 'gzip'
	},
	'css': {
		'Content-Type': 'text/css',
		'Content-Encoding': 'gzip'
	},
	'png': {
		'Content-Type': 'image/png'
	},
	'gif': {
		'Content-Type': 'image/gif'
	},
	'jpg': {
		'Content-Type': 'image/jpeg'
	}
}

def redirect(location,cookies,start_response):
	response_headers = [
		('Content-type', 'text/html; charset=utf-8'),
		('Location',location),
		('Content-Length','0')]
	for c in cookies:
		response_headers += [('Set-Cookie', c)]
	start_response('302 Redirect', response_headers)
	return ['']

# Probe function
def probe_attribute(query_string,attribute_name):
	rx = re.compile('%s=([^&]+)' % attribute_name)
	miter = rx.finditer(query_string)
	try:
		match = miter.next()
		return match.groups()[0]
	except StopIteration:
		return None

	
class PySiteApplication(object):

	def __init__(self,basedir):
		self.basedir = abspath(basedir)
		self.conf = getConfiguration(basedir)
		self.templates_dir = join(basedir,'templates')
		self.subhandlers_dir = join(basedir,'subhandlers')
		self.translations_dir = join(basedir,'translations')
		sys.path.append(basedir)
		self.rx_static_file = re.compile('.+\.(%s)$' % '|'.join(ext_map_content_type.keys()),re.I)
	
	def __call__(self,environ, start_response):
		global rx_login_id,mv_login_version
		
		log = logger(self.conf)
		status = "200 OK"
		output = ""

		path = environ['PATH_INFO'][1:]
		# Static files
		m = self.rx_static_file.match(path)
		if m:
			ext = m.groups()[0].lower()
			if exists(join(self.basedir,path)):
				fpath = join(self.basedir,path)
				log.warning(fpath)
				fstat = os.stat(fpath)
				content_size = str(fstat.st_size)
				ftypeinfo = ext_map_content_type[ext]
				response_headers = [
					('Last-Modified',strftime("%a, %d %b %Y %H:%M:%S GMT",gmtime(fstat.st_mtime))),
					('Accept-Ranges', 'bytes'),
					('Content-Type', ftypeinfo['Content-Type']) ]
				tf = None
				if 'Content-Encoding' in ftypeinfo:
					response_headers += [('Content-Encoding',ftypeinfo['Content-Encoding'])]
					tf = tempfile.mktemp()
					zf = gzip.open(tf,'wb')
					ff = open(fpath,'rb')
					data = ff.read(4096)
					while data:
						zf.write(data)
						data = ff.read(4096)
					ff.close()
					zf.close()
					fpath = tf
					content_size = str(os.stat(tf).st_size)
				response_headers += [('Content-Length',content_size)]
				start_response(status, response_headers)
				f = open(fpath,'rb')
				data = f.read(4096)
				while data:
					yield data
					data = f.read(4096)
				if tf:
					os.unlink(fpath)
				raise StopIteration

		locales = localization(self.translations_dir)
		ls = locales.lang_support()
		lang = None # Default
		default_lang = 'en'
		browser_langs = []
		if 'HTTP_ACCEPT_LANGUAGE' in environ:
			browser_langs = httpheader.parse_accept_language_header(environ['HTTP_ACCEPT_LANGUAGE'])
		for l in browser_langs:
			if lang:
				break
			for lp in l[0].parts:
				if lp in ls:
					lang = lp
					break
		if not lang:
			lang = default_lang
		mv_login_id = None
		if 'HTTP_COOKIE' in environ:
			http_cookies = environ['HTTP_COOKIE']
			mv_login_id = probe_attribute(http_cookies,rx_login_id)
		
		template = environ['PATH_INFO'][1:]
		if template=='':
			template = 'main'
		template_info = {
			'tr':{},
			'tr_common':{},
			'sitename': self.conf.sitename,
			'sitetitle': self.conf.sitetitle
		}
		template_info['supported_countries'] = [
			{'short': 'dk', 'title': u'Danmark'},
			{'short': 'se', 'title': u'Sverige'},
			{'short': 'no', 'title': u'Norge'}
		]
		template_info.update(locales.tr(lang,'common',disambiguation='school'))
		template_info.update(locales.tr(lang,template,disambiguation='school'))
		template_info['tr_common'].update(locales.tr(lang,'common',disambiguation='school'))
		template_info['tr'].update(locales.tr(lang,template,disambiguation='school'))
		
		# Request translator
		def translate(source,context=template,comment=None,lang=lang,locales=locales):
			return locales.tr(lang,context=context,source=source,disambiguation=comment)

		subhandler = None
		try:
			subhandler = imp.load_source('subhandlers.%s' % template, join(self.basedir,'subhandlers','%s.py' % template))
		except:
			log.warning(get_traceback())
			pass
		
		response_headers = []

		environ['lang_support'] = locales.lang_support
		environ['tr'] = locales.tr
		environ['logger'] = log
		environ['lang'] = lang
		init = getattr(subhandler,'init',None)
		if init:
			try:
				init(template_info,response_headers,environ,translate)
			except Exception as e:
				log.warning(get_traceback())
				raise e
		
		subhandler_redirect = getattr(subhandler,'redirect',None)
		if subhandler_redirect:
			cookies = []
			location = subhandler_redirect(template_info,cookies,environ)
			if location:
				output = redirect(location,cookies,start_response)
		
		template_info['translate'] = translate
		template = join(self.templates_dir,'%s.jinja' % template)
		if exists(template):
			jinja_temp = Template(unicode(open(template).read(),'utf-8'))
			output = jinja_temp.render(template_info).encode('utf-8')
		else:
			output = 'Template: "%s" does not exist' % template 
		
		response_headers += [
			('Content-type', 'text/html; charset=utf-8'),
			('Content-Length', str(len(output)))]
		
		start_response(status, response_headers)
		yield output

