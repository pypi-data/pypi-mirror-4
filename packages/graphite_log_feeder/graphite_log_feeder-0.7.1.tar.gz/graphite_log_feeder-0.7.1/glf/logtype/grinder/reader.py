
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
from glf.feeder.line import AbstractLineReader
from mtfileutil.reverse import reverseSeek
from glf.logtype.grinder import column_map
from glf import config_param

ALL_TRANSACTIONS = "All_Transactions"
TABLE_MARKER = "Final statistics for this process"

class LineReader(AbstractLineReader):
    """
    A line reader implementation that supports reading Grinder
    log files.
    
    This class must be named LineReader
    """
    
    def __init__ (self, config):
        """
        config is a standard python configparser
        """
        self.config = config
        map_file = config.get(config_param.GRAPHITE_SECTION, config_param.GRINDER_MAPPING_FILE)
        self.tx_num_name_map = {} # key: tx number, val: tx name
        line_name_map = {} # key: data line, val: tx name
        final_out_lines = reverseSeek (map_file, TABLE_MARKER)
        for line in final_out_lines:
            if line.find("Test") == 0 or line.find("Test") == 1 or line.startswith("Totals"):
                if line.startswith("Totals"):
                    # Format the totals line to be identical to test lines
                    line = line.replace("Totals", "Totals 0") # add a column
                    line = '%s "%s"' % (line, ALL_TRANSACTIONS)
                testName = self._get_initial_tx_name(line)
                line_name_map [line] = testName
        if len(line_name_map) == 0:
            msg = """ 
                FATAL:  Incomplete or corrupted grinder out file.  No summary data containing
                test number/name mappings found."""
            print msg
            sys.exit(1)
    
        duplicate_tx_names = self._get_duplicates(line_name_map.values())
        if len(duplicate_tx_names) > 0:
            print "Duplicate transaction names found: %s" % duplicate_tx_names
        for line in line_name_map.keys():
            tx_name = self._get_initial_tx_name(line).replace(' ', '_')
            txNum = self._get_tx_num(line)
            if duplicate_tx_names.__contains__(tx_name):
                tx_name = "%s_%s" % (tx_name, txNum)
            self.tx_num_name_map[txNum] = tx_name
            line_name_map[line] = tx_name
        print "Final tx names: %s" % self.tx_num_name_map.values()
        

    def _get_initial_tx_name(self, line):
        return line.split('"')[1]   # test names appear in quotes
    
    
    def _get_tx_num(self, line):
        return line.split(" ")[1] # test number is 2nd column   


    def _get_duplicates(self, tx_names):
        """
        Returns a subset of tx_names containing items that appear more than once
        """
        itemCountMap = {}
        for item in tx_names:
            if itemCountMap.has_key(item):
                itemCountMap[item] += 1
            else:
                itemCountMap[item] = 1
        return [ key for key in itemCountMap.keys() if itemCountMap[key] > 1]

           
    def get_timestamp(self, words):
        # example:
        # 2, 0, 1, 1321056277917, 217, 0, 302, 0, 0, 29, 97, 124
        return int(words[3][:13]) / 1000


    def get_counter_metrics(self, words):
        """
      
        TODO:   example value for 'words'
        
        TODO:  bandwidth, HTTP status codes, HTTP response errors,
               new connections
        """
        # test # is third column
        # 2, 0, 1, 1321056277917, 217, 0, 302, 0, 0, 29, 97, 124
        metrics = []
        tx_num = words[2].split(',')[0]
        base_tx_name = self.tx_num_name_map[tx_num]
        # pass or fail?
        if words[5].startswith('0'):
            metrics = [("%s_Passed" %ALL_TRANSACTIONS, 1.0)]
            metrics.append(("%s_Passed" % base_tx_name,1.0))
            # ...
            return metrics
        metrics = [("%s_Failed" %ALL_TRANSACTIONS, 1.0)]
        metrics.append(("%s_Failed" % base_tx_name, 1.0))
        #print "Counter metrics: %s" %metrics
        return metrics


    def get_timer_metrics(self, words):
        """
        Returns None if the tx failed
        Returns list of timed transactions otherwise
        
            * total response time
            * time to resolve host
            * time to establish connection
            * time to first byte
            
        """
        # Thread, Run, Test, Start time (ms since Epoch), Test time, Errors, HTTP response code, HTTP response length, HTTP response errors, Time to resolve host, Time to establish connection, Time to first byte
        # 2, 0, 1, 1321056277917, 217, 0, 302, 0, 0, 29, 97, 124
        if not words[5].startswith('0'):
            return None
        metrics = []
        tx_names = [ALL_TRANSACTIONS]
        tx_num = words[2].split(',')[0]
        tx_names.append(self.tx_num_name_map[tx_num])
        for tx in tx_names:
            metric_name = "%s" %tx
            val = float(words[4].split(',')[0])
            metrics.append((metric_name, val))
        return metrics


    def get_first_data_line(self, stream):
        # skip to the first valid line
        if not stream.readline():
            print "Invalid data file"
            sys.exit(1)
        line = stream.readline()
        if not line:
            print "Invalid data file"
            sys.exit(1)
        return line
