from datetime import timedelta
from collections import Counter, OrderedDict


def get_serviceperiod(schedule, service_date):
    (result_date, periods) = schedule.GetServicePeriodsActiveEachDate(service_date,
                                                                      service_date+timedelta(days=1))[0]
    assert result_date == service_date
    return [sp.service_id for sp in periods]

def get_childstops(schedule, parent_stop):
    stops = []
    for stop in schedule.GetStopList():
        if stop.parent_station and stop.parent_station == parent_stop.stop_id:
            stops.append(stop)
    return stops

def get_stop_by_id(schedule, stop_id):
    for stop in schedule.GetStopList():
        if stop.stop_id == stop_id:
            return stop

def get_name_for_route(schedule, route_id):
    routes = schedule.GetRouteList()
    for route in routes:
        if route.route_id != route_id:
            continue
        else:
            if route.route_short_name != "":
                return route.route_short_name
            elif route.route_long_name != "":
                return route.route_long_name
            else:
                return route_id


def find_service(schedule, target_date, target_routes, target_stopid):
    #TODO: it would be good to validate that the given stop and routes exist.
    periods = get_serviceperiod(schedule, target_date)

    target_stop = get_stop_by_id(schedule, target_stopid)
    assert target_stop is not None

    if target_stop.parent_station and target_stop.parent_station != '':
        target_stop = get_stop_by_id(schedule, target_stop.parent_station)

    target_stops = [target_stop] + get_childstops(schedule, target_stop)

    results_temp = {}

    for route in schedule.GetRouteList():
        if route.route_id in target_routes:
            count_0 = Counter()
            headsigns_0 = Counter()
            count_1 = Counter()
            headsigns_1 = Counter()
            trips = route.trips
            for trip in trips:
                if trip.service_id in periods:
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

            results_temp[route.route_id] = {'route_color': route.route_color,
                                            'route_name': get_name_for_route(schedule, route.route_id),
                                            'headsigns_0': headsigns_0,
                                            'count_0': count_0,
                                            'bins_0': [count_0.get(x, 0) for x in range(0, 24)],
                                            'headsigns_1': headsigns_1,
                                            'count_1': count_1,
                                            'bins_1': [count_1.get(x, 0) for x in range(0, 24)]}
    results = OrderedDict()

    for route_id in target_routes:
        results[route_id] = results_temp[route_id]

    return (results, target_stop.stop_name)
