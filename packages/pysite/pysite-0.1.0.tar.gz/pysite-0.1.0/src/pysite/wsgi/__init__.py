# -*- coding: utf-8 -*-
from jinja2 import Template
from os.path import dirname,normpath,join,exists
import re,cgi,sys,imp
from wsgiref.util import request_uri
from pysite.tools.log import logger,get_traceback
from pysite.localization import localization
import httpheader

rx_login_id = re.compile('mv_login_id=([-_\.a-zA-Z0-9]+)')

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
def probe_attribute(query_string,regexp):
	miter = regexp.finditer(query_string)
	try:
		match = miter.next()
		return match.groups()[0]
	except StopIteration:
		return None

class PySiteApplication(object):

	def __init__(self,basedir):
		self.basedir = basedir
		self.templates_dir = join(basedir,'templates')
		self.subhandlers_dir = join(basedir,'subhandlers')
		self.translations_dir = join(basedir,'translations')
		sys.path.append(basedir)
	
	def __call__(self,environ, start_response):
		global rx_login_id,mv_login_version
		
		log = logger(self.basedir)
		status = "200 OK"
		output = ""

		mv_login_id = probe_attribute(environ['QUERY_STRING'],rx_login_id)
		uri_parts = request_uri(environ).split('?')
		if mv_login_id:
			yield redirect(
				uri_parts[0],
				[],
				start_response)

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
		template_info = {'tr':{},'tr_common':{}}
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
				yield redirect(location,cookies,start_response)
		
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

