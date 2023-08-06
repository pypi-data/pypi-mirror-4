'''
Created on 21/May/2012

@author: Natalia Vale Asari
@note: Based Andre's starlighttable.py

'''

import os
import gzip
import bz2
import asciitable
from atpy.asciitables import read_ascii

def _getEmissionLineFitsVersion():
	return 'newfits.012408.f'


def read_newfits(self, filename):
	'''
	Read Abilio's emission line fits output file - version newfits.012408.f

	Natalia@IoA - 21/May/2012

	'''
	
	self.reset()

	if not os.path.exists(filename):
		raise Exception('File not found: %s' % filename)

	if filename.endswith('.gz'):
		f = gzip.GzipFile(filename)
	elif filename.endswith('.bz2'):
		f = bz2.BZ2File(filename)
	else:
		f = open(filename)

	self.table_name = 'emissionLines'
	self.keywords['arq_El'] = os.path.basename(filename)
	read_ascii(self, f, guess=False, Reader=asciitable.CommentedHeader)

	f.close()
	
####################################################################################################

def read_starlight(self, filename, el_read = None, el_skip = None):
	'''
	Read Cids's emission line fits output file

	William@IAA - 23/Aug/2012

	Optional keyword Arguments:
		el_read - List of emission lines to read. (Default: None reads all).
		el_skip - List of emission lines to skip. (Default: None reads all).
	
	'''
	
	self.reset()

	if not os.path.exists(filename):
		raise Exception('File not found: %s' % filename)

	if filename.endswith('.gz'):
		f = gzip.GzipFile(filename)
	elif filename.endswith('.bz2'):
		f = bz2.BZ2File(filename)
	else:
		f = open(filename)

	if(el_read != None):
		include_names = []
		for el in el_read:
			for prop in ('F', 'EW', 'vd', 'v0', 'SN', 'fc'):
				include_names.append('%s_%s' % (prop, el))
				include_names.append('sig%s_%s' % (prop, el))
	else: include_names = None

	if(el_skip != None):
		exclude_names = []
		for el in el_skip:
			for prop in ('F', 'EW', 'vd', 'v0', 'SN', 'fc'):
				exclude_names.append('%s_%s' % (prop, el))
				exclude_names.append('sig%s_%s' % (prop, el))
	else: exclude_names = None

	self.table_name = 'emissionLines'
	self.keywords['arq_El'] = os.path.basename(filename)
	#read_ascii(self, f, guess=False, Reader=asciitable.CommentedHeader)
	read_ascii(self, f, guess=False, Reader=asciitable.CommentedHeader, include_names = include_names, exclude_names = exclude_names)

	f.close()
	
####################################################################################################