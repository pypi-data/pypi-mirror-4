import unittest
import os
from glf.feeder.aggregator import GraphiteAggregator
from glf import glf_config
import datetime
import socket
from glf import config_param as param

SIMPLE_HOSTNAME = socket.gethostname().split('.')[0]

class TestAggregator(unittest.TestCase):
    
    def setUp(self):
        self.configfile = "aggregator.config"
        glf_config.create_example_config_file(self.configfile)
        self.config = glf_config.get_config([self.configfile])
        self.aggregator = GraphiteAggregator(datetime.datetime.now, self.config)
            
    def tearDown(self):
        if os.path.exists(self.configfile):
            os.remove(self.configfile)
    
    def test_get_graphite_prefix(self):
        '''
        default config settings in [graphite]
        carbon_prefix = deleteme
        carbon_suffix = grinder
        '''

        prefix = self.aggregator._get_graphite_prefix()
        expected = "%s.%s.%s" %(self.config.get(param.GRAPHITE_SECTION, param.CARBON_PREFIX),
                                SIMPLE_HOSTNAME,
                                self.config.get(param.GRAPHITE_SECTION, param.CARBON_SUFFIX))
        self.assertEqual(prefix, expected)

        self.config.remove_option(param.GRAPHITE_SECTION, param.CARBON_PREFIX)
        aggregator = GraphiteAggregator(datetime.datetime.now, self.config)
        prefix = aggregator._get_graphite_prefix()
        expected = "%s.%s" %(SIMPLE_HOSTNAME,
                             self.config.get(param.GRAPHITE_SECTION, param.CARBON_SUFFIX))
        self.assertEqual(prefix, expected)
        
        self.config.remove_option(param.GRAPHITE_SECTION, param.CARBON_SUFFIX)
        aggregator = GraphiteAggregator(datetime.datetime.now, self.config)
        prefix = aggregator._get_graphite_prefix()
        expected = SIMPLE_HOSTNAME
        self.assertEqual(prefix, expected)
        
        self.config.set(param.GRAPHITE_SECTION, param.CARBON_SUFFIX, "rodent")
        aggregator = GraphiteAggregator(datetime.datetime.now, self.config)
        prefix = aggregator._get_graphite_prefix()
        expected = SIMPLE_HOSTNAME + ".rodent"
        self.assertEqual(prefix, expected)

    def test_get_time_groups(self):
        time_groups = self.aggregator._get_time_group_ms()
        # time_group_milliseconds = 100, 200
        self.assertEqual(len(time_groups), 2)

    def test_get_time_group(self):
        # TODO: set these values based on configured time groups
        self.assertEqual(self.aggregator._get_time_group(10), "under_100_ms")
        self.assertEqual(self.aggregator._get_time_group(-10), "under_100_ms")
        self.assertEqual(self.aggregator._get_time_group(100), "100_to_200_ms")
        self.assertEqual(self.aggregator._get_time_group(150), "100_to_200_ms")
        self.assertEqual(self.aggregator._get_time_group(200), "over_200_ms")
        self.assertEqual(self.aggregator._get_time_group(2000), "over_200_ms")
        
    def test_update_counter_metric(self):
        key="something"
        value=5
        self.assertFalse(self.aggregator.counter_metric_totals.has_key(key))
        self.aggregator.update_counter_metric(key, value)
        self.assertTrue(self.aggregator.counter_metric_totals.has_key(key))
        self.assertEqual(self.aggregator.counter_metric_totals[key], value)
        self.aggregator.update_counter_metric(key)
        self.assertEqual(self.aggregator.counter_metric_totals[key], value+1)
        key="somethingsomething"
        value=8
        self.assertFalse(self.aggregator.counter_metric_totals.has_key(key))
        self.aggregator.update_counter_metric(key, value)
        self.assertTrue(self.aggregator.counter_metric_totals.has_key(key))
        self.assertEqual(self.aggregator.counter_metric_totals[key], value)

    def test_update_timer_metric(self):
        key="timed_tx"
        value=125.0 # TODO: set these values based on configured time groups
        self.assertFalse(self.aggregator.timer_metrics_totals.has_key(key))
        self.assertEqual(len(self.aggregator.time_groups.keys()), 0)
        self.aggregator.update_timer_metric(key, value)
        self.assertEqual(self.aggregator.timer_metrics_totals[key], value)
        # {'timed_tx': {'timed_tx_100_to_200_ms': 1.0}}
        self.assertEqual(len(self.aggregator.time_groups.keys()), 1)
        tx_time_groups = self.aggregator.time_groups[key]
        self.assertEqual(len(tx_time_groups), 1)
        self.assertEqual(tx_time_groups["%s_100_to_200_ms" %key], 1)
        
        self.aggregator.update_timer_metric(key, value)
        self.aggregator.update_timer_metric(key, value-100)
        self.assertEqual(len(tx_time_groups), 2)
        self.assertEqual(tx_time_groups["%s_100_to_200_ms" %key], 2)
        self.assertEqual(tx_time_groups["%s_under_100_ms" %key], 1)

    