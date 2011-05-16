from collections import Counter, OrderedDict

from sqlalchemy.orm import contains_eager

from gtfs.entity import *


def get_last_stop_name(schedule, trip):
    q = schedule.session.query(Stop.stop_name)
    q = q.join(StopTime)
    q = q.filter(StopTime.trip==trip)
    q = q.order_by(StopTime.stop_sequence.desc()).limit(1)
    return q.scalar()

def find_service(schedule, target_date, target_routes,
                 target_stopid, override_headsign=False):
    #TODO: it would be good to validate that the given stop and routes exist.
    periods = schedule.service_for_date(target_date)

    target_stop = Stop.query.filter_by(stop_id=target_stopid).one()

    if target_stop.parent is not None:
        target_stop = target_stop.parent

    target_stops = [target_stop] + target_stop.child_stations

    results_temp = {}

    st = StopTime.query
    st = st.filter(StopTime.stop.has(
        Stop.stop_id.in_([stop.stop_id for stop in target_stops])))
    st = st.join(Trip)
    st = st.join(Route)
    st = st.filter(Trip.service_period.has(
        ServicePeriod.service_id.in_(
            [period.service_id for period in periods])))
    st = st.filter(Route.route_id.in_(target_routes))
    st = st.options(contains_eager('trip'), contains_eager('trip.route'))

    for stoptime in st.all():
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

        if trip.direction_id == 0:
            count = results_temp[route_id]['count_0']
            headsigns = results_temp[route_id]['headsigns_0']
        elif trip.direction_id == 1:
            count = results_temp[route_id]['count_1']
            headsigns = results_temp[route_id]['headsigns_1']

        hour = (stoptime.arrival_time.val // 3600) % 24
        count[hour] += 1
        if override_headsign or (trip.trip_headsign is None and \
                                 stoptime.stop_headsign is None):
            headsign = get_last_stop_name(schedule, trip)
        else:
            headsign = trip.trip_headsign or stoptime.stop_headsign
        headsigns[headsign] += 1

    results = OrderedDict()

    for route_id in target_routes:
        results[route_id] = results_temp[route_id]
        r = results[route_id]
        r['bins_0'] = [r['count_0'].get(x, 0) for x in range(0, 24)]
        r['bins_1'] = [r['count_1'].get(x, 0) for x in range(0, 24)]

    return (results, target_stop.stop_name)
