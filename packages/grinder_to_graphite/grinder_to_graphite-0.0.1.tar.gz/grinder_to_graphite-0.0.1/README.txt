===================
Grinder to Graphite
===================

Overview
========

Grinder to Graphite (g2g) is a tool that analyzes the logs from
your Grinder tests, and sends the data into Graphite where it
can be visualized in a variety of ways.

Realtime test data may be sent to Graphite while your Grinder run
is in progress, or it may be sent to Graphite after your test is
completed.

Once the data is in Graphite you have a great amount of felxibility
in the types of reports and visualizations you want to generate.


Who should use g2g?
===================

Grinder users who have Graphite set up already, or who don't
mind installing it.  People who want to integrate data from 
The Grinder with data from a variety of other sources.  (OS
metrics like CPU use, application metrics like DB lookups
per second, etc.)


Who should use Grinder Analyzer instead of g2g?
===============================================

If you just want to get some fast, simple graphs from your Grinder
run, without a lot of setup hassle, Grinder Analyzer is probably
a better bet for you than g2g.  See:

http://track.sourceforge.net



Installation
============

g2g is written in Python.  The best way to install g2g is via pip.
::

    pip install grinder_to_graphite 

Once pip has installed g2g, you will need to generate a
config file, and edit it to be suitable for your
environment.  G2g comes with a command-line option to
generate a sample config file
::

    g2g -e


This will generate a file named 'g2g.sample.conf'
which you can use as the basis for creating your own
configuration.


There must be a running installation of Graphite on your
network for GLF to forward data to.  See the Graphite web site for
details on setting up and configuring Graphite

http://graphite.wikidot.com/


If you want to use the realtime feature, you will have to insall
Logster too.  

https://github.com/etsy/logster


Usage
=====

(after adjusting the values in your sample config file to be
appropriate for your environment)
::

    g2g  <config_file>

To see a full list of your options:
::

    g2g --help



Additional Resources
====================

Java/JMX counters and application-level metrics can be fed to
Graphite using the JMXTrans tool:

http://code.google.com/p/jmxtrans/

OS-level metrics (CPU, mem, etc.) can be fed to Graphite via
quickstatd or collectd (with graphite plugin)

https://bitbucket.org/travis_bear/quickstatd

