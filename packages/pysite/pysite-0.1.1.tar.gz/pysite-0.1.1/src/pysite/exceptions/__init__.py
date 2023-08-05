from ladon.exceptions.base import LadonException
import sys,os,traceback

class PySiteException(Exception):
	def __init__(self):
		Exception.__init__(self)
