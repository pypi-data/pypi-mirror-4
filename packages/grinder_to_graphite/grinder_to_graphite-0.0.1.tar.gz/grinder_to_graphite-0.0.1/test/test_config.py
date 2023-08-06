import unittest
import os
from glf import glf_config
import ConfigParser
from glf import config_param as param

class TestConfig(unittest.TestCase):
    
    def setUp(self):
        self.dotfilename = "dot.delete.me"
        self.dotfile = "%s/%s" % (glf_config.DOTDIR, self.dotfilename)
        self.configfile = "config.delete.me"
        
    def tearDown(self):
        if os.path.exists(self.dotfile):
            os.remove(self.dotfile)
        if os.path.exists(self.configfile):
            os.remove(self.configfile)
        
    def test_create_new_dotfile(self):
        self.assertFalse(os.path.exists(self.dotfile))
        glf_config.set_default_config(self.configfile, dotfile=self.dotfilename)
        self.assertTrue(os.path.exists(self.dotfile), "dot file %s not created" % self.dotfile)
        conf = open(self.dotfile).read()
        self.assertEqual(conf, self.configfile)
    
    def test_overwrite_existing_dotfile(self):
        initial_config_file = "random contents"
        glf_config.set_default_config(initial_config_file, dotfile=self.dotfilename)
        glf_config.set_default_config(self.configfile, dotfile=self.dotfilename)
        conf = open(self.dotfile).read()
        self.assertEqual(conf, self.configfile)
        
    def test_write_example_file(self):
        self.assertFalse(os.path.exists(self.configfile))
        glf_config.create_example_config_file(self.configfile)
        self.assertTrue(os.path.exists(self.configfile))
        config = ConfigParser.ConfigParser()
        config.read(self.configfile)
        self.assertEqual(config.get(param.GRAPHITE_SECTION, param.CARBON_PORT), "2003")

    def test_load_specified_config(self):
        glf_config.create_example_config_file(self.configfile)
        config = glf_config.get_config([self.configfile])
        self.assertNotEqual(None, config)
        self.assertEqual(config.get(param.GRAPHITE_SECTION, param.CARBON_PORT), "2003")
       
    def test_load_default_config_no_default(self):
        self.assertFalse(os.path.exists(self.dotfile))
        config = glf_config.get_config([], dotfilename=self.dotfile)
        self.assertEqual(None, config)
    
    def test_load_default_config_with_default(self):
        self.assertFalse(os.path.exists(self.dotfile))
        self.assertFalse(os.path.exists(self.configfile))
        glf_config.create_example_config_file(self.configfile)
        self.assertTrue(os.path.exists(self.configfile))
        glf_config.set_default_config(self.configfile, dotfile=self.dotfilename)
        self.assertTrue(os.path.exists(self.dotfile))
        config = glf_config.get_config([], dotfilename=self.dotfilename)
