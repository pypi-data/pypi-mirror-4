
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


from glf.feeder import aggregator
from glf import config_param as param


def ingest_log(line_reader, config):
    """
    Reads through the data file from start to finish.  Analyzes
    each line using the specified line analyzer
        
    Returns: timestamps for the first and last log file entries
    """
    data_file = config.get(param.DATA_SECTION, param.LOG_FILE)
    print "Reading data file %s " % data_file
    stream = open(data_file)
    line = line_reader.get_first_data_line(stream)
    start_timestamp = line_reader.get_timestamp(line.split())
    graphite_aggregator = aggregator.GraphiteAggregator(start_timestamp, config)
    words = []  # scope is required outside the loop
    while line:
        # process line
        words = line.split()
        timestamp = line_reader.get_timestamp(words)
        for tx_tuple in line_reader.get_counter_metrics(words):
            graphite_aggregator.update_counter_metric(tx_tuple[0], tx_tuple[1])
        timer_metrics = line_reader.get_timer_metrics(words)
        # a line may or may not contain timed metrics
        if timer_metrics:
            for tx_tuple in timer_metrics:
                # [0] = tx name, [1] = timing data
                graphite_aggregator.update_timer_metric(tx_tuple[0], tx_tuple[1])
        if timestamp > graphite_aggregator.report_time:
            graphite_aggregator.report_to_graphite()
        line = stream.readline()
    end_timestamp = line_reader.get_timestamp(words)
    stream.close()
    return (start_timestamp, end_timestamp)
