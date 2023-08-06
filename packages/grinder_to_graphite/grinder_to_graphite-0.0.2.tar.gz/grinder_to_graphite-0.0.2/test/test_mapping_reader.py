import unittest
from glf import glf_config
from glf.logtype.grinder.mapping_reader import MapReader
import os

HTTP_MAPPING_FILE="test/data/http.mapping"
INCOMPLETE_MAPPING_FILE="test/data/incomplete.http.mapping"

class TestMapReader(unittest.TestCase):

    def setUp(self):
        self.configfile = "config.delete.me"
        glf_config.create_example_config_file(self.configfile)
        self.config = glf_config.get_config([self.configfile])
        
    def tearDown(self):
        if os.path.exists(self.configfile):
            os.remove(self.configfile)

    def test_get_tx_names_happypath(self):
        map_reader = MapReader()
        tx_names = map_reader.get_tx_names(HTTP_MAPPING_FILE)
        self.assertGreater(len(tx_names), 1)
        
    def test_get_tx_names_no_mapping_file(self):
        map_reader = MapReader()
        with self.assertRaises(SystemExit) as cm:
            map_reader.get_tx_names("missing.file")
        self.assertEqual(cm.exception.code, 1)
        
    def test_get_tx_names_incomplete_mapping_file(self):
        map_reader = MapReader()
        with self.assertRaises(SystemExit) as cm:
            map_reader.get_tx_names(INCOMPLETE_MAPPING_FILE)
        self.assertEqual(cm.exception.code, 1)

    def test_get_duplicates(self):
        original_list = [1,2,3,4,4,5,5,5]
        map_reader = MapReader()
        new_list = map_reader._get_duplicates(original_list)
        self.assertEqual([4,5], new_list)
