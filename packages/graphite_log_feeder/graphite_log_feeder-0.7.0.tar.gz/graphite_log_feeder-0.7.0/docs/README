
OVERVIEW

Graphite Log Feeder (GLF) is a generic tool that can parse Grinder
log files, extract meaningful data, and forward it to Graphite for
visualizing.  In theory it will be simple to support many log types:
Apache, Scribe, etc.  However today the only log parser implementation
is for Grinder logs.

There is a similar tool -- Logster -- which also feeds log data
to Graphite.  However, Logster only supports realtime log analysis,
making it impossible to feed it a log from a few days (or more) in
the past.



INSTALLATION

There is no installation process.  GLF can be run directly
from the source tree or from the extracted tarball.

However, there must be a running installation of Graphite on your
network for GLF to forward data to.  See the Graphite web site for
details on setting up and configuring Graphite

http://graphite.wikidot.com/



USAGE

(after adjusting the values in settings.py to be appropriate
for your environment)

python graphite_log_feeder.py [ -m --mapping_file ] [ -d --data_file ]

(GLF can be run in Jython as well as CPython)



ADDITIONAL RESOURCES

Java/JMX counters and application-level metrics can be fed to
Graphite using the JMXTrans tool:

http://code.google.com/p/jmxtrans/

OS-level metrics (CPU, mem, etc.) can be fed to Graphite via
quickstatd or collectd (with graphite plugin)

https://bitbucket.org/travis_bear/quickstatd
