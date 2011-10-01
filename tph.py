from datetime import datetime
import ConfigParser
import sys

from gtfs import Schedule

from find_service import find_service
from plot_service import plot_service
from plot_spacing import plot_spacing

config = ConfigParser.ConfigParser()
config.read(sys.argv[1])

default_target_date = datetime.strptime(config.get('config',
                                                   'target_date'),
                                        "%Y-%m-%d").date()
default_intervals = range(0,25)                                        
                                        
if config.has_option('config', 'gtfs_db'):
    gtfs_db = config.get('config', 'gtfs_db')
else:
    gtfs_db = sys.argv[2]

# TODO: currently intervals can't wrap around midnight -- allow this 
if config.has_option('config','intervals'):
    intervals = eval(config.get('config', 'intervals'), {}, {})
else:
    intervals = default_intervals

schedule = Schedule(gtfs_db, echo=True)

for section in config.sections():
    if section != 'config':
        if config.has_option(section, 'target_date'):
            target_date = datetime.strptime(config.get(section,
                                                       'target_date'),
                                            "%Y-%m-%d").date()
        else:
            target_date = default_target_date
        if config.has_option(section, 'override_headsign'):
            override_headsign = config.getboolean(section, 'override_headsign')
        else:
            override_headsign = False
        if config.has_option(section, 'override_direction'):
            override_direction = config.getboolean(section, 'override_direction')
        else:
            override_direction = False
        target_routes = config.get(section, 'target_routes').split(',')
        target_routes = [route.strip() for route in target_routes]
        target_stopid = config.get(section, 'target_stopid')
        outfile = config.get(section, 'outfile')
        args = {}
        if config.has_option(section, 'direction_0_routes') and \
               config.has_option(section, 'direction_1_routes'):
            args['direction_0_routes'] = [route.strip() for route in \
                                          config.get(section,
                                                     'direction_0_routes').split(',')]
            args['direction_1_routes'] = [route.strip() for route in \
                                          config.get(section,
                                                     'direction_1_routes').split(',')]

        if config.has_option(section, 'direction_0_terminals') and \
               config.has_option(section, 'direction_1_terminals'):
            args['direction_0_terminals'] = [route.strip() for route in \
                                             config.get(section,
                                                        'direction_0_terminals').split(',')]
            args['direction_1_terminals'] = [route.strip() for route in \
                                             config.get(section,
                                                        'direction_1_terminals').split(',')]

        (results, target_stop_name, spacing, worstspacing) = find_service(schedule, target_date, intervals,
                                                   target_routes,
                                                   target_stopid,
                                                   override_headsign,
                                                   override_direction,
                                                   **args)
        
        plot_service(results, target_stop_name, target_date, intervals, outfile)

        plot_spacing(intervals,spacing,worstspacing)
        