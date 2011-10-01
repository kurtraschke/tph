import math

def hour_to_time(hour):
	hh = str(int(math.floor(hour)))
	if (len(hh) < 2):
		hh = ' ' + hh

	mm = str(int((hour - math.floor(hour)) * 60))
	if (len(mm) < 2): 
		mm = '0' + mm
	
	time = hh + ':' + mm
	
	return time

def plot_spacing(intervals,spacing,worstspacing):

	print 'Service period -  Spacing'
	for i in range(len(intervals)-1):
		# heuristic: if worst spacing is greater than 1.25 x median spacing, print it also
		spacingstr = str(int(spacing[i]))
		if float(worstspacing[i]) / float(spacing[i]) > 1.25:
			spacingstr = spacingstr + ' - ' + str(int(worstspacing[i]))
		spacingstr = spacingstr + ' min'
		print '%s - %s ... %s' % (hour_to_time(intervals[i]), hour_to_time(intervals[i+1]), spacingstr)
