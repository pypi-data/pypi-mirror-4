
import os
import ConfigParser
from os.path import expanduser

DOTDIR="%s/.grinder2graphite" %expanduser("~")
DEFAULT_CONFIG_POINTER="config_file"
if not os.path.isdir(DOTDIR):
    os.mkdir(DOTDIR)


def create_example_config_file(config_file="glf.sample.conf"):
    # Created in the current dir.  We can just barf on permission errors.
    stream = open(config_file, "w")
    text = """
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


######################################################################
# Graphite settings
#
# Misc. Data on the Graphite server.
######################################################################
[graphite]

# This setting should match the time per point interval defined
# on your graphite server in .../graphite/conf/storage-schemas.conf
# under the 'retentions' setting.  A setting like this:
#
# retentions = 10s:2y
#
# has a time per point interval of 10 seconds.
#
# If carbon_interval_seconds is set significantly above Graphite's time
# per point interval, there will be gaps in the graphs.  If
# carbon_interval_seconds is set significantly below Graphite's time per
# point interval, the data shown in the graphs will just be a sample from
# the total data available, and may therefore be less accurate.
carbon_interval_seconds = 20.0

# can be an IP address or FQDN.
carbon_host = localhost

carbon_port = 2003

# carbon_prefix, carbon_suffix, and this host's simple host name are
# combined to generate a mapping for this host's log data into the 
# graphite name space.
#
# Example:
#    this host is named 'qa-grinder01.host.net'
#    carbon_prefix = deleteme
#    carbon_suffix = grinder
# Data for this host will be found in Graphite under 
# 'deleteme.qa-grinder01.grinder'
#
# Both carbon_prefix and carbon_suffix may optionally be null or
# blank.
carbon_prefix = deleteme
carbon_suffix = grinder



######################################################################
# Data settings
#
# This section has only a single setting, which tells GLF which
# line reader configs to use.
######################################################################
[data]

# the file with the data to ingest into Graphite
log_file = /home/travis/qa-perf001.host.net-0-data.log



######################################################################
# Grinder settings
######################################################################
[grinder]

# comma-separated list.  report on the timer statistics that fall in
# these different groups.  Users of Grinder Analyzer will be familiar
# with this feature.
#
# Leave blank to disable this feature.  For example:
#     time_group_milliseconds =
time_group_milliseconds = 100, 200

# This will be the grinder out_* file from the Grinder run.  It is
# possible (but not recommended) to use an out_* file from a
# different run, provided it uses the exact same transaction
# numbers.
grinder_mapping_file = /home/travis/qa-perf001.host.net-0.log


    """
    stream.write(text)
    stream.close()
    print "Generated sample config file at '%s'" %config_file


def get_config(args, config_dir=DOTDIR, dotfilename=DEFAULT_CONFIG_POINTER):
    config_file = None
    if len(args) == 0:  
        print "No config file specified."
        dotfile = "%s/%s" %(config_dir, dotfilename)
        if not os.path.exists(dotfile):
            print "No default config specified."
            print dotfilename, dotfile
            return None
        stream=open(dotfile)
        config_file=stream.read()
        stream.close()
        print config_file
    else:
        config_file = args[0]
    if config_file is None:
        print "WARNING: config file not found: %s" %config_file
        return None
    if not os.path.exists(config_file):
        print "WARNING: config file not found: %s" %config_file
        return None
    if not os.access(config_file, os.R_OK):
        print "WARNING: cannot read config file '%s'" % config_file
        return None
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    print "loaded config at %s" %config_file
    return config


def set_default_config(config_file, config_dir=DOTDIR, dotfile=DEFAULT_CONFIG_POINTER):
    filename = "%s/%s" %(config_dir, dotfile)
    stream=open(filename, 'w')
    stream.write(config_file)
    stream.close()
