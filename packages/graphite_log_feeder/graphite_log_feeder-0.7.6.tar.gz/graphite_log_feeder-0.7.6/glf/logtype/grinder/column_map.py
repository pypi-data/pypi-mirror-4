
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



class GrinderNonHTTP:
    """
    Mappings for grinder 3.2 +
    example: 
    Thread, Run, Test, Start time (ms since Epoch), Test time, Errors
    0, 0, 1, 1338340786594, 1, 0
    """
    THREAD=0
    RUN=1
    TEST=2
    START_TIME=3
    TEST_TIME=4
    ERRORS=5


class GrinderHTTP:
    """
    Mappings for grinder 3.11 +

    example: 
    Thread, Run, Test, Start time (ms since Epoch), Test time, Errors, HTTP response code, HTTP response length, HTTP response errors, 
    Time to resolve host, Time to establish connection, Time to first byte, New connections
    4, 0, 1, 1351207995161, 0, 0, 0, 0, 0, 0, 0, 0, 0

    """
    THREAD=0
    RUN=1
    TEST=2
    START_TIME=3
    TEST_TIME=4
    ERRORS=5
    HTTP_RESPONSE_CODE=6
    HTTP_RESPONSE_LENGTH=7
    HTTP_RESPONSE_ERRORS=8
    RESOLVE_HOST_TIME=9
    ESTABLISH_CONNECTION_TIME=10
    FIRST_BYTE_TIME=11
    NEW_CONNECTIONS=12
