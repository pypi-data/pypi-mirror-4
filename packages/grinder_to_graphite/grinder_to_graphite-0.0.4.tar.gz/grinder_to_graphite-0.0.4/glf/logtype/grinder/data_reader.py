
# Copyright (C) 2011-2013, Travis Bear
# All rights reserved.
#
# This file is part of Graphite Log Feeder.
#
# Graphite Log Feeder is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Graphite Log Feeder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Graphite Log Feeder; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys
from glf.feeder.line import AbstractLineReader
from glf.logtype.grinder import column_map, mapping_reader
from glf import config_param as param
import os

ALL_TRANSACTIONS = "All_Transactions"

class LineReader(AbstractLineReader):
    """
    A line reader implementation that supports reading Grinder
    log files.
    
    This class must be named LineReader
    """
    
    def __init__ (self, config):
        """
        config is a standard python configparser
        """
        data_file = config.get(param.DATA_SECTION, param.LOG_FILE)
        self.is_http = self._is_grinder_log_http(data_file)
        if self.is_http:
            self.column_map = column_map.GrinderHTTP()
        else:
            self.column_map = column_map.GrinderNonHTTP()            
        map_file = config.get(param.GRINDER_SECTION, param.GRINDER_MAPPING_FILE)
        map_reader = mapping_reader.MapReader()
        self.tx_num_name_map = map_reader.get_tx_names(map_file)
        print "Final tx names: %s" % self.tx_num_name_map.values()

    def _is_grinder_log_http(self, data_file):
        if not os.path.exists(data_file):
            print "FATAL: data file '%s' not found." % data_file
            sys.exit(1)
        if not os.access(data_file, os.R_OK):
            print "FATAL: cannot read config file '%s'" % data_file
            sys.exit(1)
        stream = open(data_file)
        first_line = stream.readline()
        stream.close()
        words = first_line.split(",")
        if len(words) > 10:
            print "HTTP grinder log detected."
            return True
        print "Non-HTTP grinder log detected."
        return False
    
    
    def get_timestamp(self, words):
        # example:
        # 2, 0, 1, 1321056277917, 217, 0, 302, 0, 0, 29, 97, 124
        return int(words[3][:13]) / 1000


    def get_counter_metrics(self, words):
        """
        Handles metrics that happen a certain number of times -- i.e.
        how many passed transactions, how many bytes downloaded
        
        example value for 'words':
            words: ['34,', '0,', '1,', '1360890608890,', '6,', '0']        
        """
        # HTTP
        # test # is third column
        # Thread, Run, Test, Start time (ms since Epoch), Test time, Errors, HTTP response code, HTTP response length, HTTP response errors, Time to resolve host, Time to establish connection, Time to first byte, New connections
        # 1, 0, 10, 1360869449785, 57, 0, 200, 766, 0, 0, 3, 34, 1
        #
        # non-HTTP
        # Thread, Run, Test, Start time (ms since Epoch), Test time, Errors
        # 17, 0, 1, 1360890013806, 1095, 0
        
        metrics = []
        tx_num=0
        try:
            tx_num = words[self.column_map.TEST].split(',')[0]
        except:
            print "No metrics for %s" %words
            return metrics
        base_tx_name = self.tx_num_name_map[tx_num]
        # tx pass/fail
        if words[self.column_map.ERRORS].startswith('0'):
            metrics = [("%s_Passed" %ALL_TRANSACTIONS, 1.0)]
            metrics.append(("%s_Passed" % base_tx_name,1.0))
        else:
            metrics = [("%s_Failed" %ALL_TRANSACTIONS, 1.0)]
            metrics.append(("%s_Failed" % base_tx_name, 1.0))
        if not self.is_http:            
            return metrics
        # http response code
        http_rc = words[self.column_map.HTTP_RESPONSE_CODE].split(',')[0]
        metrics.append(("%s_http_rc_%s" %(ALL_TRANSACTIONS, http_rc), 1.0))
        metrics.append(("%s_http_rc_%s" %(base_tx_name, http_rc),1.0))
        # bytes downloaded
        bytes_downloaded = float(words[self.column_map.HTTP_RESPONSE_LENGTH].split(',')[0])
        metrics.append(("%s_bytes" %ALL_TRANSACTIONS, bytes_downloaded))
        metrics.append(("%s_bytes" %base_tx_name, bytes_downloaded))
        # new connections
        new_connections = float(words[self.column_map.NEW_CONNECTIONS].split(',')[0])
        metrics.append(("%s_new_connections" %ALL_TRANSACTIONS, new_connections))
        metrics.append(("%s_new_connections" %base_tx_name, new_connections))        
        return metrics


    def get_timer_metrics(self, words):
        """
        Returns None if the tx failed
        Returns list of timed transactions otherwise
        
            * total response time
            * time to resolve host
            * time to establish connection
            * time to first byte
            
        """
        
        # HTTP
        # test # is third column
        # Thread, Run, Test, Start time (ms since Epoch), Test time, Errors, HTTP response code, HTTP response length, HTTP response errors, Time to resolve host, Time to establish connection, Time to first byte, New connections
        # 1, 0, 10, 1360869449785, 57, 0, 200, 766, 0, 0, 3, 34, 1
        #
        # non-HTTP
        # Thread, Run, Test, Start time (ms since Epoch), Test time, Errors
        # 17, 0, 1, 1360890013806, 1095, 0
        try:
            if not words[self.column_map.ERRORS].startswith('0'):
                return None
        except:
            print "failed to inspect %s" %words
            return None
        metrics = []
        tx_num = words[self.column_map.TEST].split(',')[0]
        base_tx_name = self.tx_num_name_map[tx_num]
        # test time
        test_time = float(words[self.column_map.TEST_TIME].split(',')[0])
        metrics.append(("%s_time" %ALL_TRANSACTIONS, test_time))
        metrics.append(("%s_time" %base_tx_name, test_time))
        if not self.is_http:
            return metrics
        # resolve host time
        resolve_host_time = float(words[self.column_map.RESOLVE_HOST_TIME].split(',')[0])
        metrics.append(("%s_resolve_host_time" %ALL_TRANSACTIONS, resolve_host_time))
        metrics.append(("%s_resolve_host_time" %base_tx_name, resolve_host_time))        
        # establish connection time
        establish_connect_time = float(words[self.column_map.ESTABLISH_CONNECTION_TIME].split(',')[0])
        metrics.append(("%s_establish_connection_time" %ALL_TRANSACTIONS, establish_connect_time))
        metrics.append(("%s_establish_connection_time" %base_tx_name, establish_connect_time))        
        # first byte time
        first_byte_time = float(words[self.column_map.FIRST_BYTE_TIME].split(',')[0])
        metrics.append(("%s_first_byte_time" %ALL_TRANSACTIONS, first_byte_time))
        metrics.append(("%s_first_byte_time" %base_tx_name, first_byte_time))        
        #print "words: %s, resolve: %f, est: %f, first: %f" %(words, resolve_host_time, establish_connect_time, first_byte_time)
        return metrics


    def get_first_data_line(self, stream):
        # skip to the first valid line
        if not stream.readline():
            print "Invalid data file"
            sys.exit(1)
        line = stream.readline()
        if not line:
            print "Invalid data file"
            sys.exit(1)
        return line
