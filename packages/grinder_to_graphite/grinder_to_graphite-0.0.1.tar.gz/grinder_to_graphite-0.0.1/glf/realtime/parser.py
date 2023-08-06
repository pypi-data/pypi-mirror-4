"""
This module is an example Logster parser for Grinder logs.  It is not
a general-purpose solution, and will take some modification before
it will be useful in your particular case.
"""

from glf import glf_config
from glf.feeder import aggregator
from glf.logtype.grinder import data_reader
import sys
import time
from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException


class GrinderLogster(LogsterParser):

    def __init__(self, option_string=None):
        config = glf_config.get_config([option_string])
        if not config:
            print "FATAL: could not load config"
            sys.exit(1)
        self.line_reader = data_reader.LineReader(config)
        self.aggregator = aggregator.GraphiteAggregator(time.time(),config)
 
    def parse_line(self, line):
        if line.startswith("Thread"):
            return
        words = line.split(', ')
        for tx_tuple in self.line_reader.get_counter_metrics(words):
            self.aggregator.update_counter_metric(tx_tuple[0], tx_tuple[1])
        timer_metrics = self.line_reader.get_timer_metrics(words)
        for tx_tuple in timer_metrics:
            # [0] = tx name, [1] = timing data
            self.aggregator.update_timer_metric(tx_tuple[0], tx_tuple[1])
    
    def get_state(self, duration):
        self.aggregator.report_to_graphite()
        return []

