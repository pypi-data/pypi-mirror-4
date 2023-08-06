from distutils.core import setup

setup(
    name='graphite_log_feeder',
    version='0.7.4',
    author='Travis Bear',
    author_email='travis_bear@yahoo.com',
    keywords = "graphite grinder",
    packages=['glf',
              'glf.feeder',
              'glf.logtype',
              'glf.logtype.grinder'],
    scripts=['bin/graphite_log_feeder.py'],
    url='http://pypi.python.org/pypi/graphite_log_feeder/',
    license='LICENSE.txt',
    description='Ingests log files into Graphite where they can be visualized.',
    long_description=open('README.txt').read(),
    requires=["mtFileUtil"],
    install_requires=["mtFileUtil"]
)
