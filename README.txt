tph.py requires Python 2.7 or greater (but not Python 3), with
gtfs, numpy, and matplotlib installed.

It may be possible to install these dependencies with:
easy_install numpy matplotlib pytz 'python-dateutil<2.0'

matplotlib appears to require special handling and may not install
cleanly with easy_install; follow the matplotlib documentation for
your platform.

The gtfs library should be installed from:
https://github.com/kurtraschke/gtfs
(this is a fork of the version available on PyPI)

To apply tph.py to a GTFS feed, you will need to know the stop ID for
the target stop, as well as the route IDs for the routes serving that
station that you want to examine.

The Google GTFS Schedule Viewer
(http://code.google.com/p/googletransitdatafeed/wiki/ScheduleViewer)
may be useful in finding stop and route IDs, or you can manually
examine the feed to get the necessary information.

The gtfs library uses a pre-compiled SQLite database to store the
feed.  To generate this database, install gtfs as described above, and
run:

$ compile_gtfs -o <output file> <path to feed>

The GTFS feed can be a Zip file or directory.

This process will take an extended period of time (30 minutes is not
unreasonable for a GTFS feed from a large agency), but it speeds the
process of generating plots considerably, because the database can be
re-used for successive invocations of tph.py.

After compiling the database, create a configuration file (see
the 'samples' directory for sample configuration files, and config.rst
for documentation).
Then, run tph.py:

$ python2.7 tph.py agency.cfg <gtfs db>

If the GTFS database is not given in the configuration file (as the
gtfs_db parameter in the 'config' stanza), then it must be passed as
the second argument to tph.py.

Note that each route staza in the configuration file can optionally
contain its own target_date; this may be useful for generating plots
for weekday and weekend service in the same run.
