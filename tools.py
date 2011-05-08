from datetime import timedelta

def make_labels(rects, ax):
    for rect in rects:
        height = int(rect.get_height())
        if height == 0:
            continue
        elif (height >= 2):
            bar_text = str(height)
            yloc = rect.get_y() + (rect.get_height() / 2.0)
            xloc = rect.get_x() + (rect.get_width() / 2.0)
            ax.text(xloc, yloc, bar_text, horizontalalignment='center',
                     verticalalignment='center', color='white', weight='bold', size='x-small')


def make_top_labels(rects, ax, total):
    for rect in rects:
        bar_text = int(total[int(rect.get_x())])
        yloc = rect.get_y() + rect.get_height() + 2
        xloc = rect.get_x() + (rect.get_width() / 2.0)
        ax.text(xloc, yloc, bar_text, horizontalalignment='center',
                 verticalalignment='center', color='black', weight='bold', size='x-small')


def get_serviceperiod(schedule, service_date):
    (result_date, periods) = schedule.GetServicePeriodsActiveEachDate(service_date, service_date+timedelta(days=1))[0]
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
