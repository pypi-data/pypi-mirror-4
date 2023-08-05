# -*- coding: utf-8 -*-
from os.path import dirname,abspath,isdir,join
from os import listdir
import imp

translation_maps = {
	'no': ['no','nb','nn'],
	'dk': ['dk','da'],
	'se': ['se','sv'],
	'en': ['en','us','gb'],
	'nb': ['nb','no','nn'],
	'nn': ['nn','no','nb'],
	'sv': ['sv','se'],
	'da': ['da','dk'],
	'uk': ['uk','en','us'],
	'us': ['us','en','uk']
}

class Localization(object):
	
	def __init__(self,translations_dir):
		self.translations_dir = translations_dir
		self.translations = {}
		self.languages = []
	
	def update_translation_dict(self,lang,context):
		lang_dict = self.translations.get(lang)
		if type(lang_dict)==dict:
			context_dict = lang_dict.get(context)
			if type(context_dict)==dict:
				return context_dict
		else:
			self.translations[lang] = {}
			
		try:
			transmod = imp.load_source(context, join(self.translations_dir,lang,'%s.py' % context))
			self.translations[lang][context] = transmod.translations
		except Exception as e:
			self.translations[lang][context] = {}
		
		return self.translations[lang][context]

	def _tr(self,trans_item,source,disambiguation=None):
		dest_source = u'#' + source
		try:
			if disambiguation and type(trans_item)==dict:
				disambiguation_source = trans_item.get(disambiguation)
				if disambiguation_source:
					dest_source = disambiguation_source
				elif len(trans_item):
					dest_source = trans_item.items()[0][1]
			elif type(trans_item)==dict and len(trans_item):
				dest_source = trans_item.items()[0][1]
			elif trans_item:
				dest_source = trans_item
			return dest_source
		except:
			return dest_source

	def tr(self,lang,context,source=None,disambiguation=None):
		trans_dict = self.update_translation_dict(lang,context)
		if type(source)==str:
			# default utf-8 if incoming is str
			# FIXME: use chardet
			source = unicode(source,'utf-8')
		if source:
			trans_item = trans_dict.get(source)
			return self._tr(trans_item,source,disambiguation)
		else:
			ret_dict = {}
			for source,trans_item in trans_dict.items():
				ret_dict[source] = self._tr(trans_item,source,disambiguation)
			return ret_dict


	def lang_support(self,lang=None):
		global translation_maps
		if not len(self.languages):
			fs_elements = listdir(self.translations_dir)
			for fs_elem in fs_elements:
				if isdir(join(self.translations_dir,fs_elem)):
					self.languages += [fs_elem]
		if lang in translation_maps:
			for l in translation_maps[lang]:
				if self.languages.count(l):
					return l
		return self.languages

glob_loc = {}
def localization(translations_dir):
	global glob_loc
	if translations_dir not in glob_loc:
		glob_loc[translations_dir] = Localization(translations_dir)
	return glob_loc[translations_dir]
