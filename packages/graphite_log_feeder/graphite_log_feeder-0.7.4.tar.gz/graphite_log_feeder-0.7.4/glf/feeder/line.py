
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


class AbstractLineReader:
    
    def get_timestamp(self, words):
        raise NotImplementedError
    
    def get_counter_metrics(self, words):
        """
        return a list of tx names
        """
        raise NotImplementedError
    
    def get_timer_metrics(self, words):
        """
        return a list of dicts with key = tx name, value = timing
        data
        """
        raise NotImplementedError
    
    def _get_first_data_line(self, stream):
        """
        Log files may have one or more header lines that we want to skip.
        This default implementation assumes every line contains data,
        and returns the first line of the file
        """
        line = stream.readline()
        if not line:
            print "Invalid data file"
            sys.exit(1)
        return line

