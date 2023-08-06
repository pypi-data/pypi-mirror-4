from distutils.core import setup

setup(
    name='grinder_to_graphite',
    version='0.0.1',
    author='Travis Bear',
    author_email='travis_bear@yahoo.com',
    keywords = "graphite grinder logster logs",
    packages=['glf',
              'glf.feeder',
              'glf.logtype',
              'glf.realtime',
              'glf.logtype.grinder'],
    scripts=['bin/g2g', 'bin/lg2g'],
    url='http://pypi.python.org/pypi/graphite_log_feeder/',
    license='LICENSE.txt',
    description='Ingests log files into Graphite where they can be visualized.',
    long_description=open('README.txt').read(),
    requires=["mtFileUtil"],
    install_requires=["mtFileUtil"]
)
