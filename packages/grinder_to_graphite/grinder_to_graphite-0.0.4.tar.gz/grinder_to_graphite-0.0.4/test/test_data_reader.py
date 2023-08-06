import unittest
from glf import glf_config
from glf.logtype.grinder.data_reader import LineReader as GrinderLineReader
from glf import config_param as param
import os

HTTP_MAPPING_FILE = "test/data/http.mapping"
HTTP_DATA_FILE = "test/data/http.data"
NON_HTTP_MAPPING_FILE = "test/data/non-http.mapping"
NON_HTTP_DATA_FILE = "test/data/non-http.data"
DATA_LINE = "3, 0, 1, 1364113903424, 29, 0, 200, 177, 0, 3, 4, 13, 1"
HTTP_WORDS = DATA_LINE.split(", ")
NON_HTTP_WORDS = HTTP_WORDS[:6]


class TestDataReader(unittest.TestCase):
   
    def setUp(self):
        self.configfile = "config.delete.me"
        glf_config.create_example_config_file(self.configfile)
        config = glf_config.get_config([self.configfile])
        config.set(param.GRINDER_SECTION, param.GRINDER_MAPPING_FILE, HTTP_MAPPING_FILE)
        config.set(param.DATA_SECTION, param.LOG_FILE, HTTP_DATA_FILE)
        self.http_reader = GrinderLineReader(config)
        config.set(param.GRINDER_SECTION, param.GRINDER_MAPPING_FILE, NON_HTTP_MAPPING_FILE)
        config.set(param.DATA_SECTION, param.LOG_FILE, NON_HTTP_DATA_FILE)
        self.nohttp_reader = GrinderLineReader(config)
        
    def tearDown(self):
        if os.path.exists(self.configfile):
            os.remove(self.configfile)

    def test_is_http_log(self):
        self.assertTrue(self.http_reader._is_grinder_log_http(HTTP_DATA_FILE))
        self.assertTrue(self.http_reader.is_http)
        self.assertFalse(self.nohttp_reader.is_http)
        self.assertFalse(self.http_reader._is_grinder_log_http(NON_HTTP_DATA_FILE))
        with self.assertRaises(SystemExit) as cm:
            self.http_reader._is_grinder_log_http("nonexistent.file")
        self.assertEqual(cm.exception.code, 1)
        
         
    def test_get_timestamp(self):
        self.assertEqual(self.http_reader.get_timestamp(HTTP_WORDS), 1364113903)
    
    def test_get_http_counter_metrics(self):
        counter_metrics = self.http_reader.get_counter_metrics(HTTP_WORDS)
        self.assertEqual(counter_metrics, [
            ('All_Transactions_Passed', 1.0), 
            ('Search_No_Match_Passed', 1.0), 
            ('All_Transactions_http_rc_200', 1.0), 
            ('Search_No_Match_http_rc_200', 1.0), 
            ('All_Transactions_bytes', 177.0), 
            ('Search_No_Match_bytes', 177.0), 
            ('All_Transactions_new_connections', 1.0), 
            ('Search_No_Match_new_connections', 1.0)])
    
    def test_get_http_timer_metrics(self):
        timer_metrics = self.http_reader.get_timer_metrics(HTTP_WORDS)
        self.assertEqual(len(timer_metrics), 8)
        self.assertEqual(timer_metrics, [
            ('All_Transactions_time', 29.0), 
            ('Search_No_Match_time', 29.0), 
            ('All_Transactions_resolve_host_time', 3.0), 
            ('Search_No_Match_resolve_host_time', 3.0), 
            ('All_Transactions_establish_connection_time', 4.0), 
            ('Search_No_Match_establish_connection_time', 4.0), 
            ('All_Transactions_first_byte_time', 13.0), 
            ('Search_No_Match_first_byte_time', 13.0)])
        
    def test_get_non_http_counter_metrics(self):
        counter_metrics = self.nohttp_reader.get_counter_metrics(NON_HTTP_WORDS)
        self.assertEqual(counter_metrics, [
            ('All_Transactions_Passed', 1.0),
            ('Voldemort:_read_cached_known_key_Passed', 1.0)])

        
    def test_get_non_http_timer_metrics(self):
        timer_metrics = self.nohttp_reader.get_timer_metrics(NON_HTTP_WORDS)
        self.assertEqual(timer_metrics, [
            ('All_Transactions_time', 29.0),
            ('Voldemort:_read_cached_known_key_time', 29.0)])

