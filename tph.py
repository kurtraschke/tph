# -*- coding: utf-8 -*-

from collections import Counter, OrderedDict
from datetime import date, timedelta

import transitfeed
import matplotlib.pyplot as plt
import numpy as np

from tools import make_labels, make_top_labels, get_serviceperiod

schedule = transitfeed.Schedule()

schedule.Load("google_transit_cta")

results = OrderedDict()

target_date = date(year=2011, month=5, day=6)
periods = get_serviceperiod(schedule, target_date)
#target_routes = ['A', 'C', 'E']
#target_stopid = "A27"
#target_routes = ['A', 'B', 'C', 'D']
#target_stopid = "A24"
#target_routes = ['7','7X']
#target_stopid = "723"
#target_routes = ['4', '5', '6', '6X']
#target_stopid = "631"

target_routes = ['Blue']
target_stopid = "30374"


#target_direction = "0"

target_stop = get_stop_by_id(schedule, target_stopid)

if target_stop.parent_station != '':
    target_stop = get_stop_by_id(schedule, target_stop.parent_station)
    
target_stops = [target_stop] + get_childstops(schedule, target_stop)

routes = schedule.GetRouteList()
for route in routes:
    if route.route_id not in target_routes:
        continue
    else:
        count_0 = Counter()
        headsigns_0 = Counter()
        count_1 = Counter()
        headsigns_1 = Counter()
        trips = route.trips
        for trip in trips:
            if trip.service_id not in periods:
                continue
            else:
                if trip.direction_id == '0':
                    count = count_0
                    headsigns = headsigns_0
                elif trip.direction_id == '1':
                    count = count_1
                    headsigns = headsigns_1
                    
                stoptimes = trip.GetStopTimes()
                for stoptime in stoptimes:
                    if stoptime.stop in target_stops:
                        hour = stoptime.arrival_time.split(':')[0]
                        count[int(hour) % 24] += 1
                        headsigns[trip.trip_headsign or stoptime.stop_headsign] += 1
                #print trip
        results[route.route_id] = {'route_color': route.route_color,
                                   'headsigns_0': headsigns_0,
                                   'count_0': count_0,
                                   'bins_0': [count_0.get(x, 0) for x in range(0, 24)],
                                   'headsigns_1': headsigns_1,
                                   'count_1': count_1,
                                   'bins_1': [count_1.get(x, 0) for x in range(0, 24)]}


print results

maxtph = 60 #TODO: set this automagically

fig = plt.figure(figsize=(16,6), dpi=300)
ax = fig.add_subplot(111, xlim=(0,24), ylim=(0, maxtph))
fig.subplots_adjust(bottom = 0.2, left=0.05, right=0.98)
ind = np.arange(24)
width = 0.40

ax.set_xlabel('Hour')
ax.set_ylabel('Vehicles per Hour')
ax.set_title('Service at %s on %s' % (target_stop.stop_name, target_date.strftime("%Y-%m-%d")))
ax.set_yticks(np.arange(0, maxtph, 4))
ax.set_xticks(ind+width)
ax.set_xticklabels([str(i) for i in range(0, 24)])

color_dups = Counter()
hatch = ["/", "O", "x", "o", ".", "*"]

prev_0 = np.array(np.zeros(24))
prev_1 = np.array(np.zeros(24))

for route_id, route_data in results.items():
    plt_args = {}
    if route_data['route_color'] != '':
        plt_args['color'] = '#' + route_data['route_color']
    else:
        plt_args['color'] = '#ffffff'
    color_dups[plt_args['color']] += 1
    if color_dups[plt_args['color']] > 1:
        plt_args['hatch'] = hatch[color_dups[plt_args['color']] - 2]
    route_data['plot_0'] = ax.bar(ind, route_data['bins_0'], width, bottom=prev_0, **plt_args)
    route_data['plot_1'] = ax.bar(ind+width, route_data['bins_1'], width, bottom=prev_1, **plt_args)

    make_labels(route_data['plot_0'], ax)
    make_labels(route_data['plot_1'], ax)

    prev_0 += np.array(route_data['bins_0'])
    prev_1 += np.array(route_data['bins_1'])


last_route_data = results.values()[-1]
make_top_labels(last_route_data['plot_0'], ax, prev_0)
make_top_labels(last_route_data['plot_1'], ax, prev_1)

plt.legend([route_data['plot_0'][0] for route_data in results.values()],
           [get_name_for_route(schedule, route_id) for route_id in results.keys()])

headsigns_0 = set()
headsigns_1 = set()

for route in results.values():
    headsigns_0.update(route['headsigns_0'].keys())
    headsigns_1.update(route['headsigns_1'].keys())

import textwrap

d0 = textwrap.fill("Direction 0 is: %s" % (", ".join(headsigns_0)), 170, subsequent_indent='    ')
d1 = textwrap.fill("Direction 1 is: %s" % (", ".join(headsigns_1)), 170, subsequent_indent='    ')

plt.figtext(0.05, 0.05, d0+"\n"+d1, size="small")

plt.savefig("service.pdf")#, bbox_inches='tight')
