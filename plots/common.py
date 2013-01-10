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
import pandas as pd

def error(msg):
    print " ERROR: "+msg


# -----------------------------------------------------------------------------
def custom_stats(data, ptile_range):
    """
    Compute basic stats on Series or DataFrame
    NOTE: I didn't wanna subclass pandas classes !!
    """
    stats = None

    def quantile_as_dataframe(df, q, col):
        """
        Little helper to save lines of code: quantile over a DataFrame returns a
        series with index being df column names, and index '0'. Need to rewrite
        index and transpose.
        """
        tmp = pd.DataFrame(df.quantile(q=q/100.0), index=df.columns)
        tmp.columns = [col]
        return tmp.T

    # Series.describe() returns a Series, DataFrame.describe() returns a
    # DataFrame. In both cases, the index is made of strings descriptive of the
    # stat (eg. 'mean')
    # Add a few custom statistics to stats, returned by describe()
    if isinstance(data, pd.Series):
        stats = data.describe()
        stats = pd.concat([
            stats,
            pd.Series(data.quantile(q=1/100.0), index=['1%']),
            pd.Series(data.quantile(q=99/100.0), index=['99%']),
            pd.Series(data.quantile(q=ptile_range[0]/100.0),
                                    index=['lower_bound']),
            pd.Series(data.quantile(q=ptile_range[1]/100.0),
                                    index=['upper_bound']),
        ])

    elif isinstance(data, pd.DataFrame):
        stats = data.describe()
        stats = pd.concat([stats, quantile_as_dataframe(data, 1, '1%')])
        stats = pd.concat([stats, quantile_as_dataframe(data, 99, '99%')])
        stats = pd.concat([stats, quantile_as_dataframe(data, ptile_range[0],
            'lower_bound')])
        stats = pd.concat([stats, quantile_as_dataframe(data, ptile_range[1],
            'upper_bound')])

    else:
        raise exceptions.TypeError

    return stats



# -----------------------------------------------------------------------------
def scale_data(spread):
    """
    Automatically determine the unit and scale to convert to.
    """
    # Auto-scale data if not explicitly given
    if spread < 1e-6:
        scale = 1e9
        unit = '[ns]'
    elif spread < 1e-3:
        scale = 1e6
        unit = '[us]'
    elif spread < 1:
        scale = 1e3
        unit = '[ms]'
    else:
        scale = 1
        unit = '[s]'

    return scale, unit

