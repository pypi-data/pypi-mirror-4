import logging,logging.handlers
import traceback,imp
from StringIO import StringIO
from os.path import join


def get_traceback():
	strio = StringIO()
	traceback.print_exc(file=strio)
	return strio.getvalue()

pysite_logger = None

def logger(sitedir):
	global pysite_logger
	if not pysite_logger:
		conf = imp.load_source('conf',join(sitedir,'conf.py'))
		log_filename = 'site.log'
		if 'logfile' in conf.conf:
			log_filename = conf.conf['logfile']
		pysite_logger = logging.getLogger('mv-login')
		pysite_logger.setLevel(logging.DEBUG)

		# Add the log message handler to the logger
		if len(pysite_logger.handlers)==0:
			handler = logging.handlers.RotatingFileHandler(log_filename, maxBytes=4000000, backupCount=5)
			formatter = logging.Formatter("%(asctime)s - %(message)s")
			handler.setFormatter(formatter)
			pysite_logger.addHandler(handler)
	return pysite_logger