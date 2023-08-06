
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

import sys
import os
import ConfigParser
from glf.feeder import aggregator
from glf import config_param


def get_line_reader(config):
    line_reader = None
    reader_section = config.get(config_param.DATA_SECTION, config_param.LINE_READER) 
    line_reader_module = config.get(reader_section, config_param.LINE_READER_MODULE)
    exec "import %s" % line_reader_module
    exec "line_reader = %s.LineReader(config)" % line_reader_module 
    return line_reader


def ingest_log(line_reader, config):
    """
    Reads through the data file from start to finish.  Analyzes
    each line using the specified line analyzer
        
    Returns: timestamps for the first and last log file entries
    """
    data_file = config.get(config_param.DATA_SECTION, config_param.LOG_FILE)
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
            graphite_aggregator.update_counter_metric(timestamp, tx_tuple[0], tx_tuple[1])
        timer_metrics = line_reader.get_timer_metrics(words)
        if not timer_metrics:
            # a line may or may not contain timed metrics
            line = stream.readline()
            continue
        for tx_tuple in timer_metrics:
            # [0] = tx name, [1] = timing data
            graphite_aggregator.update_timer_metric(timestamp, tx_tuple[0], tx_tuple[1])
            
            
        line = stream.readline()
    end_timestamp = line_reader.get_timestamp(words)
    return (start_timestamp, end_timestamp)


def get_config(config_file):  
    if not os.path.exists(config_file):
        print "FATAL: config file '%s' not found." % config_file
        sys.exit(1)
    if not os.access(config_file, os.R_OK):
        print "FATAL: cannot read config file '%s'" % config_file
        sys.exit(1)
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    return config



