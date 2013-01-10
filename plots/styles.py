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


class PlotStyles(object):
    """
    Class to represent plot options, a.k.a. styles.
    """

    def __init__(self, style_dict=None):
        self._colors = dict()
        self._linestyles = dict()

        if style_dict != None:
            if not isinstance(style_dict, dict) == True:
                raise exceptions.TypeError
            self.add_styles(style_dict)

    def add_styles(self, styles):
        for key, tval in styles.items():
            if not isinstance(tval, tuple) == True:
                raise exceptions.TypeError
            self._colors[key] = tval[0]
            self._linestyles[key] = tval[0]+tval[1]


    def valid_for_data(self, data):
        '''
        Check that style dictionary keys match a dataframe column or series
        name.
        '''
        # Get keys of data as series or column names
        if isinstance(data, pd.Series):
            dkeys = set([data.name])
        elif isinstance(data, pd.DataFrame):
            dkeys = set(data.columns)
        else:
            raise exceptions.TypeError

        # colors and linestyles share same keys by construction
        color_keys = set(self._colors.keys())
        if (not dkeys.issubset(color_keys)):
            print dkeys
            print color_keys
            print "styles and data keys do not match"
            return False
        else:
            return True


    def color_for_name(self, name):
        return self._colors[name]

    def linestyle_for_name(self, name):
        return self._linestyles[name]

    def linestyles(self):
        return self._linestyles

