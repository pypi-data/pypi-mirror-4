#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.dom.minidom as minidom
import pprint,re,os,sys

def parse_ts(ts_fname):
	doc = minidom.parse(open(ts_fname))
	tr_dict = {}
	ts_elem = doc.getElementsByTagName('TS')[0]
	lang = ts_elem.getAttribute('language')
	for ctx_elem in doc.getElementsByTagName('context'):
		name = ctx_elem.getElementsByTagName('name')[0]
		context = name.childNodes[0].data
		tr_dict[context] = {}
		for msg_elem in ctx_elem.getElementsByTagName('message'):
			src_elem = msg_elem.getElementsByTagName('source')
			if not len(src_elem):
				continue
			source = src_elem[0].childNodes[0].data
			if source not in tr_dict[context]:
				tr_dict[context][source] = {}

			comment = u''
			c_elem = msg_elem.getElementsByTagName('comment')
			if len(c_elem):
				comment = c_elem[0].childNodes[0].data
			if comment not in tr_dict[context][source]:
				tr_dict[context][source][comment] = {}
			
			translation = None
			tr_elem = msg_elem.getElementsByTagName('translation')
			if len(tr_elem):
				if len(tr_elem[0].childNodes):
					translation = tr_elem[0].childNodes[0].data
				tr_dict[context][source][comment]['type'] = None
				if tr_elem[0].hasAttribute('type'):
					tr_dict[context][source][comment]['type'] = tr_elem[0].getAttribute('type')
			tr_dict[context][source][comment]['translation'] = translation
			
			filename = None
			line = None
			l_elem = msg_elem.getElementsByTagName('location')
			if len(l_elem):
				filename = l_elem[0].getAttribute('filename')
				line = l_elem[0].getAttribute('line')
			tr_dict[context][source][comment]['filename'] = filename
			tr_dict[context][source][comment]['line'] = line
	return lang,tr_dict


def lrelease(ts_fname):
	lang,tr_dict = parse_ts(ts_fname)
	basedir = os.path.dirname(ts_fname)
	if not os.path.exists(basedir):
		os.makedirs(basedir)
	for context,sources in tr_dict.items():
		translations = {}
		for source,comments in sources.items():
			translations[source] = {}
			for comment,trinfo in comments.items():
				if trinfo['translation']:
					translations[source][comment] = trinfo['translation']
			if not len(translations[source]):
				del translations[source]
		f = open('%s/%s.py' % (basedir,context),'w')
		f.write('''# -*- coding: utf-8 -*-

translations = ''')
		pprint.pprint(translations,f)
		f.close()

if __name__=='__main__':
	if len(sys.argv)<2:
		sys.stderr.write("usage: %s <ts-file>\n" % sys.argv[0])
		sys.stderr.write("Example: %s admin_da.ts\n" % sys.argv[0])
		sys.exit(1)
	lrelease(sys.argv[1])


