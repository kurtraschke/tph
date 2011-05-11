tph.py requires Python 2.7 or greater (but not Python 3), with
transitfeed, numpy, and matplotlib installed.

It may be possible to install these dependencies with:
easy_install transitfeed numpy matplotlib pytz 'python-dateutil<2.0'

matplotlib appears to require special handling and may not install
cleanly with easy_install

To apply tph.py to a GTFS feed, you will need to know the stop ID for
the target stop, as well as the route IDs for the routes serving that
station that you want to examine.

The Google GTFS Schedule Viewer
(http://code.google.com/p/googletransitdatafeed/wiki/ScheduleViewer)
may be useful in finding stop and route IDs, or you can manually
examine the feed to get the necessary information. 

Once you have the stop and route IDs, create a configuration file (see
nyct.cfg, wmata.cfg, and cta.cfg in this directory for examples), and
run tph.py:

$ python2.7 tph.py agency.cfg

Note that each route staza in the configuration file can optionally
contain its own target_date; this may be useful for generating plots
for weekday and weekend service in the same run.

tph.py requires that certain optional elements be present in the GTFS
feed:
* Trips must use the direction_id field

Finally, do not be alarmed by long runtimes; transitfeed takes >5
minutes to load large GTFS feeds. After the feed is loaded, each
additional plot only adds a few seconds of processing time.
