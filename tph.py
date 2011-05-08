# -*- coding: utf-8 -*-

from datetime import date
import pickle

import transitfeed

from find_service import find_service
from plot_service import plot_service




target_date = date(year=2011, month=5, day=6)
#target_routes = ['A', 'C', 'E']
#target_stopid = "A27"
#target_routes = ['A', 'B', 'C', 'D']
#target_stopid = "A24"
#target_routes = ['7','7X']
#target_stopid = "723"
target_routes = ['4', '5', '6', '6X']
target_stopid = "631"

#target_routes = ['Brn', 'P', 'Org', 'G', 'Pink']
#target_stopid = "30074"


"""schedule = transitfeed.Schedule()
schedule.Load("../google_transit")
(results, target_stop_name) = find_service(schedule, target_date, target_routes, target_stopid)
pickle.dump((results, target_stop_name, target_date), open("servicedump", "w"))"""

(results, target_stop_name, target_date) = pickle.load(open("servicedump"))

print results

plot_service(results, target_stop_name, target_date, "service.pdf")
