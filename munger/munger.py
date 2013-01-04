#/usr/bin/env python
#
# ------------------------------------------------------------------------------
# Copyright (c) 2012, Matt Davis  <matt@synclab.org>
# Copyright (c) 2012, Julien Ridoux <julien@synclab.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ------------------------------------------------------------------------------

import exceptions
import re
import pandas as pd
import numpy as np

from container import *


class DataMerger(object):

	MERGE_RADCLOCK = 1
	MERGE_UDP = 2


	@classmethod
	def merge(cls, left, right):
		merge_op = 0
		for container in (left,right):
			assert(isinstance(container, DataContainer))
			if container.mtype == 'radclock':
				merge_op = cls.MERGE_RADCLOCK
			elif container.mtype == 'UDP_merged':
				merge_op = cls.MERGE_UDP

		if merge_op == cls.MERGE_RADCLOCK:
			return cls.merge_radclock(left, right)
		elif merge_op == cls.MERGE_UDP:
			return cls.merge_udp(left, right)
		else:
			print 'Cannot figure out what you are trying to merge'
			raise exception.TypeError


	@classmethod
	def merge_radclock(cls, left, right):
		
		if left.mtype == 'radclock' and right.mtype == 'RAD_merged':
			radclock = left
			stamps = right
		elif right.mtype == 'radclock' and left.mtype == 'RAD_merged':
			radclock = right
			stamps = left
		else:
			print 'Cannot container types in merge_radclock'
			raise exception.TypeError

		stamps.data['key'] = stamps.data['Tf']

		radclock.data['key'] = radclock.data['Tf']
		fields = radclock.fields
		# Tb will be a duplicate after merge, remove it now (otherwise pandas will
		# change its name
		fields.remove('Tb')
		fields.append('key')
		fields.remove('Tf')
		radclock.data = radclock.data[fields]

		# Important: a pandas merge on column DISCARDS indexes. Very annoying.
		merged = pd.merge(stamps.data, radclock.data, on='key', how='inner', sort=False)

		# Reindex using time and clean up extra columns
		merged.index = merged.time

		fields = list(merged.columns)
		fields.remove('key')
		fields.remove('time')
		merged = merged[fields] 

		# Remove first 2 lines, it is often a bit dodgy there
		merged = merged.ix[2:]

		return merged


