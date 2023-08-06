#!/usr/bin/env python

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


import datetime
from optparse import OptionParser
import sys
from glf import engine
from glf import config_param as param


def usage():
    print """
    usage:  graphite_log_feeder [options] config_file
    
    options include:
        -d, --data-file:
                            path to the log file to ingest.  Overrides
                            the 'log_file' setting in the config file.
                            
        -e, --create_example_config_file-config-file:
                            writes an create_example_config_file configuration file to
                            standard out.  You can modify this create_example_config_file
                            to suit your own needs.
                            
    config_file:
                            path to the file with the graphite_log_feeder
                            settings.  If you don't have a config file, 
                            run 'graphite_log_feeder -e' to get one.
    """
    sys.exit(1)

    



def create_example_config_file():
    sample_config_file = "glf.sample.conf"
    # Created in the current dir.  We just barf on permission errors.
    stream = open(sample_config_file, "w")
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

# The only line reader currently available is the Grinder's.  The
# value specified here ('grinder') must appear as a section head
# in this config file.  We satisfy that requirement in the
# [grinder] section, below.
line_reader = grinder

# the file with the data to ingest into Graphite
log_file = /home/travis/qa-perf001.host.net-0-data.log



######################################################################
# Grinder settings
######################################################################
[grinder]

# Users should not change this value.
line_reader_module = glf.logtype.grinder.reader

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
    print "Generated sample config file at '%s'" %sample_config_file
    sys.exit()
    
    
def main():
    parser = OptionParser()
    parser.add_option("-m", "--mapping_file",
                      dest="mapping_file",
                      help="Grinder out* file with tx name/num mapings",
                      metavar="FILE")
    parser.add_option("-e", "--example-config-file", action="store_true", dest="example")
    parser.add_option("-d", "--data-file",
                      dest="data_file",
                      help="grinder data file",
                      metavar="FILE")
    (options, args) = parser.parse_args()
    if options.example:
        create_example_config_file()
    if len(args) == 0:
        usage()
    config_file = args[0]
    config = engine.get_config(config_file)
    if options.data_file:
        config.set("data", "log_file", options.data_file) 
    if options.mapping_file:
        config.set("grinder", "grinder_mapping_file", options.mapping_file)
    print "Ingesting log file '%s'.  Forwarding data to graphite host at '%s'" % (config.get(param.DATA_SECTION, param.LOG_FILE),
                                                                                  config.get(param.GRAPHITE_SECTION, param.CARBON_HOST))
    times = engine.ingest_log (engine.get_line_reader(config), config)
    print "Finished log ingestion.  Log data start: %d (%s), Log data end: %d (%s)" % (times[0],
                                                                              datetime.datetime.fromtimestamp(times[0]),
                                                                              times[1],
                                                                              datetime.datetime.fromtimestamp(times[1]))


if __name__ == "__main__":
    main()
