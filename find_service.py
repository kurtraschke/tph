from collections import Counter, OrderedDict

from tools import get_serviceperiod, get_stop_by_id, get_childstops, get_name_for_route


def find_service(schedule, target_date, target_routes, target_stopid):
    periods = get_serviceperiod(schedule, target_date)

    target_stop = get_stop_by_id(schedule, target_stopid)

    if target_stop.parent_station != '':
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
