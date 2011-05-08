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
    stops = [parent_stop]
    for stop in schedule.GetStopList():
        if stop.parent_station == parent_stop:
            stops.append(stop.stop_id)
    return stops
