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

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import *

from common import *

# Used with vectorize to create an array of base**elt.  
def power_array(elt, base):
	return pow(base,elt) 


def compute_allanvar(ts, smoothed=True):

	max_scale = floor(log(ts.count(),2)) - 1	# Why -1?
	vpow = np.vectorize(power_array)
	T = vpow(np.arange(1, max_scale, 1), 2)
	# TODO Isn't this line redundant with the -1 trick?
	T = T[T<=ts.count()/2]				# need at least 2 points at largest T

	variances = np.zeros(len(T))
	stdvar    = np.zeros(len(T))

	# for smoothing, need at least 3 points to avoid edge effect
	if smoothed:
		 Ts = T[T<=len(ts)/3];
		 smoothedvar    = np.zeros(len(Ts))
		 smoothedstdvar = np.zeros(len(Ts))


	# Convert to numpy array
	intdata = ts.cumsum()
	vpow = np.vectorize(pow)

	if smoothed == False:
		# Variance for each aggregation level
		for i in range(len(T)):
			scale = T[i]
			# Select indices in cumsum vector, with indices[0] = 0
			indices = range(int(scale), int(ts.count()), int(scale))
			# Aggregated series at scale 'scale', need to have x[0] = 0
			x = pd.Series([0])
			x = x.append(intdata.ix[indices] / scale)
			x = x.diff().ix[1:]
			if len(x) > 1:
				variances[i] = (vpow(x.diff().ix[1:], 2) / (len(x) - 1) / 2).sum()
		# TODO: values computed are not the same as the Matlab ones, will need
		# to check what is going on here ... wondering if it is a rounding
		# issue??
		# print variances

	else:
		# Smoothed variance for each aggregation level
		for i in range(len(Ts)):
			scale = T[i]
			# calculate over the T different origins
			for origin in range(int(scale)):
				# first result already done, no need to calculate
				if origin == 0:
					indices = range(int(scale), int(ts.count()), int(scale))
				else:
					indices = range(origin-1, int(ts.count()), int(scale))

					# no longer need data(0)=0, now data(origin-1)
					x = pd.Series([0])
					x = x.append(intdata.ix[indices] / scale)
					x = x.diff().ix[1:]
					# calc Allan Var
					variances[i] = (vpow(x.diff().ix[1:], 2) / (len(x) - 1) / 2).sum()
				# accumulate at each origin
				smoothedvar[i] = smoothedvar[i] + variances[i];
			# take the average
			smoothedvar[i] = smoothedvar[i]/T[i];

	if smoothed == True:
		variances = smoothedvar

	return T, variances



# -----------------------------------------------------------------------------
# Plot Allan Variance
# -----------------------------------------------------------------------------
def allanvar(ts, ax=None, title='Title', color='b',
		transparency=0.3, path=None):
	"""
	Routine to generate Allan variance.
	"""

	# Ttest that ts is a pandas Series object
	if not isinstance(ts, pd.Series) and not isinstance(ts, pd.DataFrame):
		print "Data passed to histogram is not a pandas Series or DataFrame"
		return

	T, var = compute_allanvar(ts)

	s = np.diff(ts.index.asi8) # intervals as nanoseconds.
	period = round(np.median(s) * 1e-9)

	# Get reasonable figure and axis
	# NOTE: saving to a file takes precedence on axis being specified
	if path != None or ax == None:
		fig = plt.figure(figsize=(5, 3.50)) # in inches!
		ax = fig.gca()

	plt.loglog(T*period, np.sqrt(var/period), 'r-', label=ts.name)

	# Esthetics
	ax.grid(which='both', axis='both')
	ax.legend()
	ax.set_title(title)
#	ax.set_xlabel(xlabel+ ' ' +unit+ ' (min=%.1f, med=%.1f, IQR=%.1f)'
#			%(scaledstats['min'], scaledstats['50%'],
#				scaledstats['75%']-scaledstats['25%']))


	# To have ticks and labels display nicely
	fig.tight_layout()

	# Saving on file
	if path != None:
		fig.savefig(path)

	# Return not scaled stats
	return var

