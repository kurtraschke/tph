# -*- coding: utf-8 -*-

from datetime import datetime
import ConfigParser
import sys

import transitfeed

from find_service import find_service
from plot_service import plot_service


config = ConfigParser.ConfigParser()
config.read(sys.argv[1])

default_target_date = datetime.strptime(config.get('config', 'target_date'), "%Y-%m-%d").date()
gtfs_dir = config.get('config', 'gtfs_dir')

schedule = transitfeed.Schedule()
schedule.Load(gtfs_dir)

for section in config.sections():
    if section != 'config':
        if config.has_option(section, 'target_date'):
            target_date = datetime.strptime(config.get(section, 'target_date'), "%Y-%m-%d").date()
        else:
            target_date = default_target_date
        target_routes = config.get(section, 'target_routes').split(',')
        target_stopid = config.get(section, 'target_stopid')
        outfile = config.get(section, 'outfile')
        (results, target_stop_name) = find_service(schedule, target_date, target_routes, target_stopid)
        plot_service(results, target_stop_name, target_date, outfile)
