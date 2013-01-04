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
import matplotlib.pyplot as plt

from common import *
from styles import *


# -----------------------------------------------------------------------------
# Plot histograms
# -----------------------------------------------------------------------------
def hist(ts, styles=None, ax=None, ptile_range=(0,100), title='Title', color='b',
		transparency=0.3, unit_scale=('s', 0), xlabel='XLabel',
		with_yticks=True, with_kde=True, path=None):
	"""
	Convenience function that wraps a few common tasks to generate an
	histogram based on pandas Series object. It uses pandas.hist(), which in
	turns relies on matplotlib.hist().
	styles parameter takes precedence over color and transparency.
	"""

	# Ttest that ts is a pandas Series object
	if not isinstance(ts, pd.Series):
		print "Data passed to histogram is not a pandas Series object"
		return

	# Check that style dictionary keys match df column names
	if styles != None:
		if styles.valid_for_data(ts) == False:
			raise exceptions.KeyError

	# Get stats for this data as a Series
	stats = custom_stats(ts, ptile_range)

	# Auto-scale data if not explicitly given
	if unit_scale[1] == 0:
		spread = stats['99%'] - stats['1%']
		scale, unit = scale_data(spread)
	else:
		unit  = '['+unit_scale[0]+']'
		scale = unit_scale[1]

	# Scale stats
	scaledstats = stats * scale

	# Get reasonable figure and axis
	# NOTE: saving to a file takes precedence on axis being specified
	if path != None or ax == None:
		fig = plt.figure(figsize=(5, 3.50)) # in inches!
		ax = fig.gca()
	else:
		fig = plt.gcf()

	if styles != None:
		plot_color = styles.color_for_name(ts.name)
	else:
		plot_color = color

	# Actual histogram
	# TODO: cap bin size?
	(ts * scale).hist(ax=ax, bins=500,
		alpha=transparency,
		facecolor=plot_color,
		edgecolor=plot_color,
		linewidth=0,
		normed=True,
		range=(scaledstats['lower_bound'],scaledstats['upper_bound']),
		label=''
#		label=ts.name
	)

	# Gaussian kernel density estimation
	if with_kde == True:
		(ts * scale).plot(ax=ax, kind='kde', style='k--', label='')

	# Esthetics
	ax.grid(which='major', axis='both')
	ax.set_xlim(scaledstats['lower_bound'],scaledstats['upper_bound'])
#	ax.legend()
	ax.set_title(title)
	ax.set_xlabel(xlabel+ ' ' +unit+ ' (min=%.1f, med=%.1f, IQR=%.1f)'
			%(scaledstats['min'], scaledstats['50%'],
				scaledstats['75%']-scaledstats['25%']))

	if with_yticks == False:
		ax.set_yticks([])
		ax.set_yticklabels('')
		ax.set_ylabel('')

	# To have ticks and labels display nicely
	if fig == None:
		print "Warning: no figure, no tight layout"
	else:
		fig.tight_layout()
		print 'Warning: disabled histogram tight layout'

	# Saving on file
	if path != None:
		fig.savefig(path)

	# Return not scaled stats
	return stats

