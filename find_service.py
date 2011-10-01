from collections import Counter, OrderedDict

from sqlalchemy.orm import contains_eager, eagerload

from gtfs.entity import *

from numpy import median, inf

import math

def get_last_stop_id(schedule, trip):
    q = schedule.session.query(StopTime.stop_id)
    q = q.filter(StopTime.trip == trip)
    q = q.order_by(StopTime.stop_sequence.desc()).limit(1)
    return q.scalar()


def get_last_stop_name(schedule, trip):
    q = schedule.session.query(Stop.stop_name)
    q = q.join(StopTime)
    q = q.filter(StopTime.trip == trip)
    q = q.order_by(StopTime.stop_sequence.desc()).limit(1)
    return q.scalar()

def find_interval(intervals, val):
    # returns index of interval corresponding to time value passed in. 
    # returns -1 for times before first interval or after last interval
    arrival_hours = math.fmod(val / 3600., 24.)
    
    intervalidx = -1
    for j in range(len(intervals)-1):
        if (intervals[j] <= arrival_hours < intervals[j+1]):
            intervalidx = j
            break
    return intervalidx

def find_service(schedule, target_date, intervals, target_routes,
                 target_stopid, override_headsign=False,
                 override_direction=False,
                 direction_0_routes=[], direction_1_routes=[],
                 direction_0_terminals=[], direction_1_terminals=[]):

    #TODO: it would be good to validate that the given stop and routes exist.
    periods = schedule.service_for_date(target_date)

    # combine stop with its parent (if any) and children of parent
    target_stop = Stop.query.filter_by(stop_id=target_stopid).one()
    if target_stop.parent is not None:
        target_stop = target_stop.parent
    target_stops = [target_stop] + target_stop.child_stations

    # identify which routes use frequency, and which use stoptimes
    frequency_routes = []
    for route_id in target_routes:
        if Trip.query.filter(Trip.route_id == route_id).first().uses_frequency:
            frequency_routes.append(route_id)
    all_routes = target_routes
    stoptime_routes = set(target_routes) - set(frequency_routes)

    # initialize results tables
    results_temp = {}
    intervallist = []
    for i in range(len(intervals)):
        intervallist.append([])
    spacing = [inf] * len(intervals)
    worstspacing = [inf] * len(intervals)
    laststval = -1;
    
    # process a stoptime, storing data for its associated route in counters headsigns and count
    def process_stoptime(stoptime, surrogate_time=None):
        route = stoptime.trip.route
        route_id = route.route_id

        if route_id not in results_temp:
            results_temp[route_id] = {'route_color': route.route_color,
                                      'route_type': route.route_type,
                                      'route_name': route.route_short_name or \
                                      route.route_long_name or route.route_id,
                                      'headsigns_0': Counter(),
                                      'count_0': Counter(),
                                      'headsigns_1': Counter(),
                                      'count_1': Counter()}

        trip = stoptime.trip

        if route_id in direction_0_routes or \
               get_last_stop_id(schedule, trip) in direction_0_terminals or \
               (trip.direction_id == 0 and not override_direction):
            count = results_temp[route_id]['count_0']
            headsigns = results_temp[route_id]['headsigns_0']
        elif route_id in direction_1_routes or \
                 get_last_stop_id(schedule, trip) in direction_1_terminals or \
                 (trip.direction_id == 1 and not override_direction):
            count = results_temp[route_id]['count_1']
            headsigns = results_temp[route_id]['headsigns_1']
        else:
            raise Exception("No direction available for trip %s on route %s." % (trip.trip_id, route_id))

        intervalidx = find_interval(intervals, (surrogate_time or stoptime.arrival_time.val))
        if intervalidx != -1:
            count[intervalidx] += 1
            if override_headsign or (trip.trip_headsign is None and \
                                     stoptime.stop_headsign is None):
                headsign = get_last_stop_name(schedule, trip)
            else:
                headsign = trip.trip_headsign or stoptime.stop_headsign
            headsigns[headsign] += 1

    # iterate over stoptime routes           
    if len(stoptime_routes) > 0:
        st = StopTime.query
        st = st.filter(StopTime.stop.has(
            Stop.stop_id.in_([stop.stop_id for stop in target_stops])))
        st = st.join(Trip)
        st = st.join(Route)
        st = st.filter(Trip.service_id.in_(periods))
        st = st.filter(Route.route_id.in_(target_routes))
        st = st.options(contains_eager('trip'), contains_eager('trip.route'))

        for stoptime in st.all():
            process_stoptime(stoptime)
            
            # assuming stoptimes are iterated in order
            # skip 1st when computing interval since last stoptime
            if laststval != -1:
                intervalidx = find_interval(intervals,stoptime.arrival_time.val)
                if intervalidx != -1:
                    intervallist[intervalidx].append((stoptime.arrival_time.val - laststval) / 60)
            laststval = stoptime.arrival_time.val 

    # iterate over frequency routes           
    if len(frequency_routes) > 0:
        st = StopTime.query
        st = st.filter(StopTime.stop.has(
            Stop.stop_id.in_([stop.stop_id for stop in target_stops])))
        st = st.join(Trip)
        st = st.join(Route)
        st = st.filter(Trip.service_id.in_(periods))
        st = st.filter(Route.route_id.in_(frequency_routes))
        st = st.options(contains_eager('trip'), contains_eager('trip.route'),
                        eagerload('trip.frequencies'))

        for exemplar_stoptime in st.all():
            frequencies = exemplar_stoptime.trip.frequencies
            offset = exemplar_stoptime.elapsed_time
            for frequency in frequencies:
                for trip_time in frequency.trip_times:
                    process_stoptime(exemplar_stoptime, trip_time + offset)

                    intervalidx = find_interval(intervals,trip_time + offset)
                    intervallist[intervalidx].append(offset/60)

    results = OrderedDict()

    # combine routes over directions and bin over intervals
    for route_id in all_routes:
        if route_id not in results_temp:
            raise Exception("No data generated for route_id %s. Does it exist in the feed?" % route_id)
        results[route_id] = results_temp[route_id]
        r = results[route_id]
        #r['bins_0'] = [r['count_0'].get(x, 0) for x in range(0, 24)]
        #r['bins_1'] = [r['count_1'].get(x, 0) for x in range(0, 24)]
        r['bins_0'] = [r['count_0'].get(x, 0) for x in range(len(intervals)-1)]
        r['bins_1'] = [r['count_1'].get(x, 0) for x in range(len(intervals)-1)]

    for ival in range(len(intervallist)):
        if len(intervallist[ival]) > 0:
            spacing[ival] = median(intervallist[ival])
            worstspacing[ival] = max(intervallist[ival])

    return (results, target_stop.stop_name, spacing, worstspacing)
