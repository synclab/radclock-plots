#/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (C) 2012 Julien Ridoux <julien@synclab.org>
# -----------------------------------------------------------------------------

import exceptions
import re
import pandas as pd
import numpy as np

from datetime import datetime as dtime
from dateutil import tz


# Took a while to get it right (right being relative to pandas and numpy
# versions and other silly things.
# datetime class as a micro-sec resolution.
# numpy64 can do better, but cannot find how to convert UNIX stamp to
# datetime64 without using strptime(), which only specify mus accuracy
def stamp_parser(stamp):
	return dtime.utcfromtimestamp(np.float64(stamp)).replace(tzinfo=tz.tzutc())


class DataLoader(object):

	# Types for data. Key is original data type, and value is the new type
	# resulting from a merge_into_left when left data has type key
	mergeTypes = {
			'NTP_dag'        : 'NTP_dag_merged',
			'NTP_rad'        : 'RAD_merged',
			'UDP_dag'        : '',
			'UDP_sniff'      : 'UDP_merged',
			'NTP_sniff_snd'  : 'NTP_rad',
			'NTP_sniff_rcv'  : '',
			'NTP_dag_merged' : '',
			'RAD_merged'     : '',
			'UDP_merged'     : '',
			'radclock'       : ''
			}


	def __init__(self, datafile, mtype=None):
		"""
		Generic class to open stamp data files. Main purpose of the constructor is
		to extract header and data from files created by radclock, dag_extract or
		udp_probes_sniffer.
		"""
		self.data = pd.DataFrame()

		# Set data type
		if mtype not in DataLoader.mergeTypes and mtype is not None:
			raise exceptions.TypeError
		else:
			self.mtype = mtype

		# Store opened file desc if passed by argparse for example, otherwise
		# assumes path and attempt to open it.
		# TODO: should surcharge __del__ to close file descriptor.
		if hasattr(datafile, 'read'):
			self.dataFile = datafile
			self.to_close = False
		else:
			try:
				f = open(datafile, 'r')
				self.dataFile = f
				self.to_close = True
			except:
				print 'Could not open path '+datafile
				raise



	def extract_header(self, comment='%'):
		"""
		Extract header from data file and store it in StringIO. Comment
		character passed as a parameter.
		"""
		self.header = list()
		self.dataFile.seek(0)
		for line in self.dataFile:
			if line.startswith(comment):
				self.header.append(line)
			else:
				break


	def parse_header(self):
		"""
		Extract exact fields descriptor from header
		"""
		self.headerlen = 0
		for line in self.header:
			if line.startswith('% description:'):
				self.description = line.replace('% description: ', '')
				self.description = re.sub(r'\n', '', self.description)

			if line.startswith('% type:'):
				mtype = line.replace('% type: ', '')
				mtype = re.sub(r'\n', '', mtype)
				if self.mtype != mtype:
					print 'Data type mismatch %s %s' % (self.mtype, mtype)
					raise exceptions.TypeError

			if line.startswith('% version:'):
				version = line.replace('% version: ', '')
				version = re.sub(r'\n', '', version)
				self.version = int(version)

			if line.startswith('% fields:'):
				# Clean up fields string and build fields descriptors
				fields = line.replace('% fields: ', '')
				fields = re.sub(r'\n', '', fields)
				fields = fields.split(r' ')
				self.fields_from_text = fields
				self.fields = list(self.fields_from_text)

			if line.startswith('% magic:'):
				magic = line.replace('% magic: ', '')
				magic = re.sub(r'\n', '', magic)
				self.magic = magic

			if line.startswith('%'):
				self.headerlen += 1

			if not line.startswith('%'):
				break

		if len(fields) == 0:
			print 'Could not find format from header'
			raise exceptions.TypeError


	def load_data(self):
		"""
		Extract tabular stamp data as a pandas.DataFrame.
		"""
		# Extract file header, takes comment character as an option
		self.extract_header()
		self.parse_header()

		# Pandas infers the type of data automatically, and 
		# maps data to float64 or int64. Problem, may arise when integers are
		# way too big (eg NTP key) and uses the full 64 bit range. Pandas
		# convert unsigned to signed, leading to negative and non unique number.
		# Should be fine on merged data (since keys are dropped), but something
		# to keep in mind if raw timestamps get too big?
		self.dataFile.seek(0)
		self.data = pd.read_csv(self.dataFile, delimiter= ' ',
				skiprows=self.headerlen, names=self.fields,
				parse_dates={'time' : [5]},
				keep_date_col=True,
				date_parser=stamp_parser)
		self.data = self.data[:-1]



