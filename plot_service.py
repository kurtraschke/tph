from collections import Counter
import textwrap
import math

import numpy as np
from matplotlib.backends.backend_pdf import FigureCanvasPdf
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure


def make_labels(rects, ax, color='white'):
    for rect in rects:
        height = int(rect.get_height())
        if (height >= 2):
            bar_text = str(height)
            yloc = rect.get_y() + (rect.get_height() / 2.0)
            xloc = rect.get_x() + (rect.get_width() / 2.0)
            ax.text(xloc, yloc, bar_text, horizontalalignment='center',
                    verticalalignment='center', color=color,
                    weight='bold', size='x-small')


def make_top_labels(rects, ax, total):
    for rect in rects:
        bar_text = int(total[int(rect.get_x())])
        yloc = rect.get_y() + rect.get_height() + 1
        xloc = rect.get_x() + (rect.get_width() / 2.0)
        ax.text(xloc, yloc, bar_text, horizontalalignment='center',
                verticalalignment='center', color='black',
                weight='bold', size='x-small')


def mode_string(route_types):
    mode_vehicle_names = ['Trains', 'Trains', 'Trains',
                          'Buses', 'Boats', 'Cars', 'Cars', 'Trains']

    if (len(set(route_types)) > 1):
        #vehicle types differ
        vehicle_name = 'Vehicles'
    else:
        try:
            vehicle_name = mode_vehicle_names[int(route_types[0])]
        except (IndexError, ValueError):
            vehicle_name = 'Vehicles'

    return "%s per hour" % (vehicle_name)


def contrasting_color(input_color):
    r = int(input_color[0:2], 16)
    g = int(input_color[2:4], 16)
    b = int(input_color[4:6], 16)

    r_scale = r / 255.0
    g_scale = g / 255.0
    b_scale = b / 255.0

    if max(r_scale, g_scale, b_scale) > 0.5:
        (new_r, new_g, new_b) = (0, 0, 0)
    else:
        (new_r, new_g, new_b) = (255, 255, 255)

    return "{:02x}{:02x}{:02x}".format(new_r, new_g, new_b)


def plot_service(results, target_stop_name, target_date, intervals, outfile):
    maxinterval = len(intervals)-1
    interval_durations = np.array(np.zeros(maxinterval))
    for i in range(maxinterval):
        interval_durations[i] = intervals[i+1] - intervals[i] 
    
    fig_format = outfile[-3:]

    fig = Figure(figsize=(12, 6), dpi=300)
    if fig_format == 'pdf':
        canvas = FigureCanvasPdf(fig)
    elif fig_format == 'svg':
        canvas = FigureCanvasSVG(fig)
    ax = fig.add_subplot(111, xlim=(0, maxinterval))
    fig.subplots_adjust(bottom=0.2, left=0.05, right=0.98)

    pos = np.arange(maxinterval)
    width = 0.40

    color_dups = Counter()
    hatch = ["/", ".", "x", "*", "+"]

    values_0 = np.array(np.zeros(maxinterval))
    values_1 = np.array(np.zeros(maxinterval))

    for route_id, route_data in results.items():
        bar_args = {}
        if route_data['route_color'] and route_data['route_color'] != '':
            bar_args['color'] = '#' + route_data['route_color']
        else:
            bar_args['color'] = '#000000'
            bar_args['edgecolor'] = '#444444'
        color_dups[bar_args['color']] += 1
        if color_dups[bar_args['color']] > 1:
            (hatch_dup, hatch_id) = divmod(color_dups[bar_args['color']] - 2,
                                           len(hatch))
            bar_args['hatch'] = hatch[hatch_id] * (hatch_dup + 1)

        # MSC something's wrong with variable durations?
        norm_bins_0 = np.array(route_data['bins_0']) / interval_durations
        norm_bins_1 = np.array(route_data['bins_1']) / interval_durations
        
        route_data['plot_0'] = ax.bar(pos, norm_bins_0, width,
                                      bottom=values_0, **bar_args)
        route_data['plot_1'] = ax.bar(pos + width, norm_bins_1, width,
                                      bottom=values_1, **bar_args)
        
        make_labels(route_data['plot_0'], ax,
                    '#' + contrasting_color(bar_args['color'][1:]))
        make_labels(route_data['plot_1'], ax,
                    '#' + contrasting_color(bar_args['color'][1:]))

        values_0 += norm_bins_0
        values_1 += norm_bins_1
    
    if len(results) > 1:
        last_route_data = results.values()[-1]
        make_top_labels(last_route_data['plot_0'], ax, values_0)
        make_top_labels(last_route_data['plot_1'], ax, values_1)

    maxtph = (math.ceil(max(max(values_0),
                            max(values_1)) / 10.0) * 10) + 5
    
    ax.set_ylim(0, maxtph)
    ax.set_xlabel('Period')
    ax.set_ylabel(mode_string(
        [route['route_type'] for route in results.values()]))
    ax.set_title('Service at %s on %s' % (target_stop_name,
                                          target_date.strftime("%Y-%m-%d")))
    ax.set_yticks(np.arange(0, maxtph, 4))
    ax.set_xticks(pos + width)
    ax.set_xticklabels([str(i) for i in intervals[0:maxinterval]]) #for i in range(0, len(intervals))
    ax.legend([route_data['plot_0'][0] for route_data in results.values()],
              [route_data['route_name'] for route_data in results.values()],
              prop={'size': 'small'}, ncol=2)

    headsigns_0 = set()
    headsigns_1 = set()

    for route in results.values():
        headsigns_0.update(route['headsigns_0'].keys())
        headsigns_1.update(route['headsigns_1'].keys())

    d0 = textwrap.fill("Direction 0 is: %s" % (", ".join(headsigns_0)),
                       150, subsequent_indent='    ')
    d1 = textwrap.fill("Direction 1 is: %s" % (", ".join(headsigns_1)),
                       150, subsequent_indent='    ')

    fig.text(0.05, 0.05, d0 + "\n" + d1, size="small")

    fig.savefig(outfile, format=fig_format)
