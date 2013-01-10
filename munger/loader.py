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

from datetime import datetime as dtime
from dateutil import tz

from container import *


# Took a while to get it right (right being relative to pandas and numpy
# versions and other silly things.
# datetime class as a micro-sec resolution.
# numpy64 can do better, but cannot find how to convert UNIX stamp to
# datetime64 without using strptime(), which only specify mus accuracy
def stamp_parser(stamp):
    return dtime.utcfromtimestamp(np.float64(stamp)).replace(tzinfo=tz.tzutc())


class DataLoader(object):

    def __init__(self, datafile):
        """
        Generic class to open stamp data files. Main purpose of the constructor is
        to extract header and data from files created by radclock, dag_extract or
        udp_probes_sniffer.
        """

        self.header = list()
        self.headerlen = 0

        # Store opened file desc if passed by argparse for example, otherwise
        # assumes path and attempt to open it.
        # TODO: should surcharge __del__ to close file descriptor.
        if hasattr(datafile, 'read'):
            self.datafile = datafile
            self.to_close = False
        else:
            try:
                fdesc = open(datafile, 'r')
                self.datafile = fdesc
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
        self.datafile.seek(0)
        for line in self.datafile:
            if line.startswith(comment):
                self.header.append(line)
            else:
                break



    def parse_header(self):
        """
        Extract exact fields descriptor from header
        """
        self.headerlen = 0
        description = ''
        fields = ''
        magic = ''
        mtype = ''
        version = ''

        for line in self.header:
            if line.startswith('% description:'):
                description = line.replace('% description: ', '')
                description = re.sub(r'\n', '', description)

            if line.startswith('% fields:'):
                # Clean up fields string and build fields descriptors
                fields = line.replace('% fields: ', '')
                fields = re.sub(r'\n', '', fields)
                fields = fields.split(r' ')

            if line.startswith('% magic:'):
                magic = line.replace('% magic: ', '')
                magic = re.sub(r'\n', '', magic)

            if line.startswith('% type:'):
                mtype = line.replace('% type: ', '')
                mtype = re.sub(r'\n', '', mtype)

            if line.startswith('% version:'):
                version = line.replace('% version: ', '')
                version = re.sub(r'\n', '', version)

            if line.startswith('%'):
                self.headerlen += 1

            if not line.startswith('%'):
                break

        if len(list(fields)) == 0:
            print 'Could not find format from header'
            raise exceptions.TypeError


        header_info = dict()
        header_info['description'] = description
        header_info['fields'] = list(fields)
        header_info['fields_from_text'] = fields
        header_info['magic'] = magic
        header_info['mtype'] = mtype
        header_info['version'] = int(version)
        return header_info


    def load_data(self, container):
        """
        Extract tabular stamp data as a pandas.DataFrame.
        """

        # Extract file header, takes comment character as an option
        self.extract_header()
        header_info = self.parse_header()

        if container.mtype != header_info['mtype']:
            print 'Data type mismatch %s %s' % (container.mtype,
                                                header_info['mtype'])
            raise exceptions.TypeError

        container.description = header_info['description']
        container.fields_from_text = header_info['fields_from_text']
        container.fields = header_info['fields']
        container.magic = header_info['magic']
        container.version = header_info['version']

        # Pandas infers the type of data automatically, and maps data to float64
        # or int64. Problem, may arise when integers are way too big (eg NTP
        # key) and uses the full 64 bit range. Pandas convert unsigned to
        # signed, leading to negative and non unique number.  Should be fine on
        # merged data (since keys are dropped), but something to keep in mind if
        # raw timestamps get too big?
        self.datafile.seek(0)

        data = pd.read_csv( self.datafile, delimiter= ' ',
                            skiprows=self.headerlen, names=container.fields,
                            parse_dates={'time' : [5]},
                            keep_date_col=True,
                            date_parser=stamp_parser)
        container.data = data[:-1]



    @classmethod
    def load(cls, datafile, container):

        # Set data type
        assert(container.mtype in DataContainer.mergeTypes)

        loader = DataLoader(datafile)
        loader.load_data(container)

