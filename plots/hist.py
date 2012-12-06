#/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (C) 2012 Julien Ridoux <julien@synclab.org>
# -----------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt

from common import *


# -----------------------------------------------------------------------------
# Plot histograms
# -----------------------------------------------------------------------------
def hist(ts, ax=None, ptile_range=(0,100), title='Title', color='b',
		transparency=0.3, unit_scale=('s', 0), xlabel='XLabel',
		with_yticks=True, with_kde=True, path=None):
	"""
	Convenience function that wraps a few common tasks to generate an
	histogram based on pandas Series object. It uses pandas.hist(), which in
	turns relies on matplotlib.hist().
	"""

	# Ttest that ts is a pandas Series object
	if not isinstance(ts, pd.Series):
		print "Data passed to histogram is not a pandas Series object"
		return

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

	# Actual histogram
	# TODO: cap bin size?
	(ts * scale).hist(ax=ax, bins=500,
		alpha=transparency,
		facecolor=color,
		edgecolor=color,
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
	ax.legend()
	ax.set_title(title)
	ax.set_xlabel(xlabel+ ' ' +unit+ ' (min=%.1f, med=%.1f, IQR=%.1f)'
			%(scaledstats['min'], scaledstats['50%'],
				scaledstats['75%']-scaledstats['25%']))

	if with_yticks == False:
		ax.set_yticks([])
		ax.set_yticklabels('')
		ax.set_ylabel('')

	# To have ticks and labels display nicely
	fig.tight_layout()

	# Saving on file
	if path != None:
		fig.savefig(path)

	# Return not scaled stats
	return stats

