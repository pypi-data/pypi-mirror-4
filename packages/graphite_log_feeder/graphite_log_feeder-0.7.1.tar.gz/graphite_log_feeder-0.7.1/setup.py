from distutils.core import setup

setup(
    name='graphite_log_feeder',
    version='0.7.1',
    author='Travis Bear',
    author_email='travis_bear@yahoo.com',
    keywords = "graphite grinder",
    packages=['glf','glf.logtype.grinder', 'glf.feeder'],
    scripts=['bin/graphite_log_feeder.py'],
    url='http://pypi.python.org/pypi/graphite_log_feeder/',
    license='LICENSE.txt',
    description='Ingests log files into Graphite where they can be visualized.',
    long_description=open('README.txt').read(),
    requires=["mtfileutil"]
)
