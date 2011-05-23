====================================
``tph.py`` configuration file format
====================================

``tph.py`` is driven by a configuration file which lists the plots to be generated from a GTFS feed.  This file documents the configuration file format.

Core configuration
==================

The configuration file should start with a ``config`` section.

The ``config`` section has one required parameter, ``target_date``, which must contain the date used in generating plots, in YYYY-MM-DD format.

The location of the GTFS feed database can also be specified in the ``gtfs_db`` parameter; if it is not given in the configuration file, then it must be given on the command line.

Generating plots
================

Each plot is specified in its own section in the configuration file; the name of the section is irrelevant, but must be unique. There are three required parameters:

``target_routes``
  Comma-separated list of route IDs to include in the plot
``target_stopid``
  Stop ID to use; if it is a child stop, then the parent stop and all siblings will be included
``outfile``
  Output file; either PDF or SVG.

The ``target_date`` parameter can also be given for individual plots, in which it will override the global value.

If the feed does not use direction_id
------------------------------------

If the feed does not use the direction_id field for trips, there are two options, depending on the structure of the feed.

* If every trip for a given route operates in the same direction, then use the ``direction_0_routes`` and ``direction_1_routes`` configuration parameters.  Both parameters take a comma-separated list of route IDs.

* If trips in both directions are commingled in the same route, then use the ``direction_0_terminals`` and ``direction_1_terminals`` configuration parameters.  Both parameters take a comma-separated list of destination stop IDs.

The two sets of parameters given above can be combined depending on the situation.

If the feed's direction values are invalid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the feed contains values for direction_id, but those values are unusable—meaning that all trips, regardless of actual direction, are set to either 0 or 1, then set ``override_direction``, and follow the directions above to force a valid direction for each trip.

If the feed does not use headsigns
----------------------------------

If the feed does not provide headsigns, either in the trips or stoptimes, then a headsign will be synthesized from the name of the last stop of the trip.  This behavior can be forced by setting the ``override_headsign`` parameter.
