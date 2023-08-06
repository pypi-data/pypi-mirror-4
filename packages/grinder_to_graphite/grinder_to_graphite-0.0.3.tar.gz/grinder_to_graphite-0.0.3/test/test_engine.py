import unittest
from glf import engine, glf_config
from glf.logtype.grinder.data_reader import LineReader as GrinderLineReader
from glf import config_param

HTTP_MAPPING_FILE="test/data/example_http.mapping"

class TestEngine(unittest.TestCase):

    def setUp(self):
        pass

    '''
    def test_get_line_reader(self):
        config_file="config.delete.me"
        glf_config.create_example_config_file(config_file)
        config = glf_config.get_config([config_file])
        config.set("grinder", config_param.GRINDER_MAPPING_FILE, HTTP_MAPPING_FILE)
        config.set(config_param.DATA_SECTION, config_param.LOG_FILE, "/etc/hosts") # we only need for this file to exist
        reader = engine.get_line_reader(config)
        self.assertTrue(isinstance(reader, GrinderLineReader))
    '''
