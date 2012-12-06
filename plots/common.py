#/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (C) 2012 Julien Ridoux <julien@synclab.org>
# -----------------------------------------------------------------------------

import exceptions
import pandas as pd

def error(msg):
	print " ERROR: "+msg


# -----------------------------------------------------------------------------
# Compute basic stats on Series or DataFrame
# NOTE: I didn't wanna subclass pandas classes !!
# -----------------------------------------------------------------------------
def custom_stats(p, ptile_range):

	stats = None

	# Little helper to save lines of code: quantile over a DataFrame returns a
	# series with index being df column names, and index '0'. Need to rewrite
	# index and transpose.
	def quantile_as_dataframe(df, q, col):
		tmp = pd.DataFrame(df.quantile(q=q/100.0), index=df.columns)
		tmp.columns = [col]
		return tmp.T

	# Series.describe() returns a Series, DataFrame.describe() returns a
	# DataFrame. In both cases, the index is made of strings descriptive of the
	# stat (eg. 'mean')
	# Add a few custom statistics to stats, returned by describe()
	if isinstance(p, pd.Series):
		stats = p.describe()
		stats = pd.concat([
			stats,
			pd.Series(p.quantile(q=1/100.0), index=['1%']),
			pd.Series(p.quantile(q=99/100.0), index=['99%']),
			pd.Series(p.quantile(q=ptile_range[0]/100.0), index=['lower_bound']),
			pd.Series(p.quantile(q=ptile_range[1]/100.0), index=['upper_bound']),
		])

	elif isinstance(p, pd.DataFrame):
		stats = p.describe()
		stats = pd.concat([stats, quantile_as_dataframe(p, 1, '1%')]);
		stats = pd.concat([stats, quantile_as_dataframe(p, 99, '99%')]);
		stats = pd.concat([stats, quantile_as_dataframe(p, ptile_range[0],
			'lower_bound')]);
		stats = pd.concat([stats, quantile_as_dataframe(p, ptile_range[1],
			'upper_bound')]);

	else:
		raise exceptions.TypeError

	return stats




# -----------------------------------------------------------------------------
# Compute timescale based on data spred (eg IQR)
# -----------------------------------------------------------------------------
def scale_data(spread):
	# Auto-scale data if not explicitly given
	if spread < 1e-6:
		scale = 1e9
		unit = '[ns]'
	elif spread < 1e-3:
		scale = 1e6
		unit = '[mus]'
	elif spread < 1:
		scale = 1e3
		unit = '[ms]'
	else:
		scale = 1
		unit = '[s]'

	return scale, unit

