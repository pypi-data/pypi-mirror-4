from pysite.exceptions import PySiteException

class ConfException(PySiteException):
	def __init__(self,details):
		super(ConfException,self).__init__()
		self.details = details
	
	def __str__(self):
		return self.details
