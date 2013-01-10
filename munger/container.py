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


class DataContainer(object):

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


    def __init__(self, mtype=None):
        """
        Generic class to open stamp data files. Main purpose of the constructor is
        to extract header and data from files created by radclock, dag_extract or
        udp_probes_sniffer.
        """
        self.data = pd.DataFrame()
        self.fields = list()

        # Set data type
        if mtype not in DataContainer.mergeTypes and mtype is not None:
            raise exceptions.TypeError
        else:
            self.mtype = mtype



class DataRadclock(DataContainer):

    def raw_rtt(self):
        df = self.data
        s = df.RTT
        s.name = 'raw_rtt'
        return s

    def rtt(self):
        df = self.data
        s = df.RTT * df.phat
        s.name = 'rtt'
        return s

    def rtt_host(self):
        df = self.data
        s = df.RTT * df.phat - (df.DAG_RX - df.DAG_TX)
        s.name = 'rtt_host'
        return s

    def server_delay(self):
        df = self.data
        s = df.Te - df.Tb
        s.name = 'server_delay'
        return s

