from collections import Counter, OrderedDict

from sqlalchemy.orm import contains_eager, eagerload

from gtfs.entity import *


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


def find_service(schedule, target_date, target_routes,
                 target_stopid, override_headsign=False,
                 override_direction=False,
                 direction_0_routes=[], direction_1_routes=[],
                 direction_0_terminals=[], direction_1_terminals=[]):

    #TODO: it would be good to validate that the given stop and routes exist.
    periods = schedule.service_for_date(target_date)

    if len(periods) == 0:
        raise DateNotFoundError(target_date)

    target_stop = Stop.query.filter_by(stop_id=target_stopid).one()

    if target_stop.parent is not None:
        target_stop = target_stop.parent

    target_stops = [target_stop] + target_stop.child_stations

    results_temp = {}

    frequency_routes = []

    for route_id in target_routes:
        if Trip.query.filter(Trip.route_id == route_id).first().uses_frequency:
            frequency_routes.append(route_id)

    all_routes = target_routes

    stoptime_routes = set(target_routes) - set(frequency_routes)

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
               (len(direction_0_terminals) > 0 and get_last_stop_id(schedule, trip) in direction_0_terminals) or \
               (trip.direction_id == 0 and not override_direction):
            count = results_temp[route_id]['count_0']
            headsigns = results_temp[route_id]['headsigns_0']
        elif route_id in direction_1_routes or \
                 (len(direction_1_terminals) > 0 and get_last_stop_id(schedule, trip) in direction_1_terminals) or \
                 (trip.direction_id == 1 and not override_direction):
            count = results_temp[route_id]['count_1']
            headsigns = results_temp[route_id]['headsigns_1']
        else:
            raise NoDirectionFoundError(trip.trip_id, route_id)

        hour = ((surrogate_time or stoptime.arrival_time.val) // 3600) % 24
        count[hour] += 1
        if override_headsign or (trip.trip_headsign is None and \
                                 stoptime.stop_headsign is None):
            headsign = get_last_stop_name(schedule, trip)
        else:
            headsign = trip.trip_headsign or stoptime.stop_headsign
        headsigns[headsign] += 1

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


    results = OrderedDict()

    for route_id in all_routes:
        if route_id not in results_temp:
            raise RouteNotFoundError(route_id)
        results[route_id] = results_temp[route_id]
        r = results[route_id]
        r['bins_0'] = [r['count_0'].get(x, 0) for x in range(0, 24)]
        r['bins_1'] = [r['count_1'].get(x, 0) for x in range(0, 24)]

    return (results, target_stop.stop_name)

class DateNotFoundError(Exception):
    def __init__(self, date):
        self.date = date
    def __str__(self):
        return "No service periods found for target date %s" % self.date

class RouteNotFoundError(Exception):
    def __init__(self, route):
        self.route = route
    def __str__(self):
        return "No data generated for route %s" % self.route

class NoDirectionFoundError(Exception):
    def __init__(self, trip_id, route_id):
        self.trip_id = trip_id
        self.route_id = route_id
    def __str__(self):
        return "No direction available for trip %s on route %s." % (self.trip_id, self.route_id)
