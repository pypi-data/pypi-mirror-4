
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

import socket
import sys
from glf import config_param as param

# 'spandex.mycompany.com' becomes 'spandex'
SIMPLE_HOSTNAME = socket.gethostname().split('.')[0]

class GraphiteAggregator:
    
    def __init__(self, start_timestamp, config):
        self.config = config
        self._reset_report(start_timestamp)
        self.graphite_prefix = self._get_graphite_prefix()
        # generate time group names
        self.time_group_milliseconds = self._get_time_group_ms()
        self.time_group_names = []
        if len(self.time_group_milliseconds) == 0:
            print "No time groups specified."
            return
        self.time_group_names += ["under_%d_ms" % self.time_group_milliseconds[0]]
        if len(self.time_group_milliseconds) > 1:
            for i in range (1, len(self.time_group_milliseconds)):
                self.time_group_names += ["%d_to_%d_ms" % (
                    self.time_group_milliseconds[i - 1], self.time_group_milliseconds[i])]
        self.time_group_names += [
                "over_%d_ms" % self.time_group_milliseconds[len(self.time_group_milliseconds) - 1] ]
        print "Initialized aggregator.  Reporting every %d seconds of data to %s" %(
            config.getfloat(param.GRAPHITE_SECTION, param.CARBON_INTERVAL_SECONDS),
            config.get(param.GRAPHITE_SECTION, param.CARBON_HOST))
        print "Time groups: %s" % self.time_group_names
        print "Data mapping: %s" %self.graphite_prefix


    def _get_graphite_prefix(self):
        gp = SIMPLE_HOSTNAME
        carbon_prefix = None
        carbon_suffix = None
        try:
            carbon_prefix = self.config.get(param.GRAPHITE_SECTION, param.CARBON_PREFIX)
        except:
            pass
        try:
            carbon_suffix = self.config.get(param.GRAPHITE_SECTION, param.CARBON_SUFFIX)
        except:
            pass
        if carbon_prefix and carbon_prefix != "":
            gp = "%s.%s" %(carbon_prefix, gp)
        if carbon_suffix and carbon_suffix != "":
            gp = "%s.%s" %(gp, carbon_suffix)
        return gp


    def _get_time_group_ms(self):
        tgm = []
        config_tgm = self.config.get(param.GRINDER_SECTION, param.TIME_GROUP_MILLISECONDS)
        if config_tgm:
            words = config_tgm.split(",")
            for word in words:
                tgm.append(float(word.strip()))
        return tgm
        
        
    def _reset_report(self, timestamp):
        self.counter_metric_totals = {} # key: metric name, value: cumulative counter value
        self.timer_metrics_totals = {} # key: metric name, value: cumulative timer value
        self.timer_metrics_entries = {} # key: metric name, value: number of entries for this timer
        self.time_groups = {} # key: metric name, value:  {tg_name ("click_under_20_ms"), total_entries}
        self.report_time = timestamp

        
    def update_counter_metric(self, tx_name, val=1.0):
        if not self.counter_metric_totals.has_key(tx_name):
            self.counter_metric_totals[tx_name] = 0.0
        self.counter_metric_totals[tx_name] += val


    def _get_time_group(self, tx_time):
        for i in range (0, len(self.time_group_milliseconds)):
            if tx_time < self.time_group_milliseconds [i]:
                return self.time_group_names[i]
        return self.time_group_names[len(self.time_group_milliseconds)]
        
        
    def update_timer_metric(self, tx_name, tx_time):
        # 
        # mean time
        #
        if not self.timer_metrics_totals.has_key(tx_name):
            self.timer_metrics_totals[tx_name] = 0.0
        self.timer_metrics_totals [tx_name] += tx_time
        if not self.timer_metrics_entries.has_key(tx_name):
            self.timer_metrics_entries[tx_name] = 0.0
        self.timer_metrics_entries [tx_name] += 1.0
        #
        # time groupings
        #
        if len (self.time_group_milliseconds) > 0:
            time_group_name = "%s_%s" % (tx_name, self._get_time_group(tx_time))
            if not self.time_groups.has_key(tx_name):
                self.time_groups [tx_name] = {}
            if not self.time_groups [tx_name].has_key(time_group_name):
                self.time_groups [tx_name][time_group_name] = 0.0
            self.time_groups [tx_name][time_group_name] += 1.0
            
    
    def report_to_graphite(self):
        carbon_host = self.config.get(param.GRAPHITE_SECTION, param.CARBON_HOST)
        carbon_port = self.config.getint(param.GRAPHITE_SECTION, param.CARBON_PORT)
        print "Reporting to graphite (%s:%d) at %d" % (carbon_host, carbon_port, self.report_time)
        graphite = socket.socket()

        try:
            graphite.connect((carbon_host, carbon_port))
        except:
            print "FATAL: could not connect to Graphite host %s on port %d" %(carbon_host, carbon_port)
            sys.exit(1)
        #
        # Report the counters
        # (calculate mean values per second)
        #
        for counter in self.counter_metric_totals.keys():
            # graphite data format: "metric_path value timestamp\n"
            metric_path = "%s.%s" % (self.graphite_prefix, counter)
            metric_value = self.counter_metric_totals[counter] / self.config.getfloat(param.GRAPHITE_SECTION,
                                                                                      param.CARBON_INTERVAL_SECONDS)
            graphite.sendall("%s %f %d\n" % (metric_path, metric_value, self.report_time))
            #print "    %s %f %d" % (metric_path, metric_value, self.report_time)
        #
        # Report the timers
        # (calculate mean)
        #
        for timer_name in self.timer_metrics_totals.keys():
            # mean
            metric_path = "%s.%s" % (self.graphite_prefix, timer_name)
            mean_value = self.timer_metrics_totals[timer_name] / self.timer_metrics_entries[timer_name]
            graphite.sendall("%s %f %d\n" % (metric_path, mean_value, self.report_time))
            #print "   %s %f %d" % (metric_path, mean_value, self.report_time)
        
        # calculate time groupings
        for tx_name in self.time_groups.keys():
            # get group total
            group_total=0
            for time_group in self.time_groups[tx_name].keys():
                group_total += self.time_groups [tx_name][time_group]
            for time_group in self.time_groups[tx_name].keys():
                rate = self.time_groups [tx_name][time_group] / group_total
                metric_path = "%s.%s" % (self.graphite_prefix, time_group)
                graphite.sendall("%s %f %d\n" % (metric_path, rate, self.report_time))
                #print "%s %f %d" % (metric_path, rate, self.report_time)

        # clean up            
        graphite.close()
        self._reset_report(self.report_time + self.config.getfloat(param.GRAPHITE_SECTION,
                                                                   param.CARBON_INTERVAL_SECONDS))
