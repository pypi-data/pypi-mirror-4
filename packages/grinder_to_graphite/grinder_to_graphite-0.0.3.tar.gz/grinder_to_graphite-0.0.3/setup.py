from distutils.core import setup

setup(
    name='grinder_to_graphite',
    version='0.0.3',
    author='Travis Bear',
    author_email='travis_bear@yahoo.com',
    keywords = "graphite grinder logster logs",
    packages=['glf',
              'glf.feeder',
              'glf.logtype',
              'glf.realtime',
              'glf.logtype.grinder'],
    scripts=['bin/g2g', 'bin/lg2g'],
    url='https://bitbucket.org/travis_bear/grinder_to_graphite',
    license='LICENSE.txt',
    description='Ingests data from Grinder logs into Graphite where it can be visualized.',
    long_description=open('README.txt').read(),
    requires=["mtFileUtil"],
    install_requires=["mtFileUtil"]
)
