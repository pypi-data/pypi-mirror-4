from pysite.exceptions.conf import *
import imp

class PySiteConfiguration(object):
	def __init__(self,sitename=None,sitetitle=None,logfile=None):
		if sitename:
			self.sitename = sitename
			
		if not getattr(self,'sitename',None):
			raise ConfException('Mandatory configuration member "sitename" is missing')
		
		if sitetitle:
			self.sitetitle = sitetitle
		elif not getattr(self,'sitetitle',None):
			self.sitetitle = self.sitename

		if logfile:
			self.logfile = logfile
		elif not getattr(self,'logfile',None):
			self.logfile = '%s.log' % self.sitename

global_conf = None

def getConfiguration(conffile=None):
	global global_conf
	if not global_conf:
		confmod = imp.load_source('conf',conffile)
		global_conf = confmod.siteconf()
	return global_conf