from skylinespolyencode import SkyLinesPolyEncoder
import math, os
from collections import namedtuple

FlightPathFix = namedtuple('FlightPathFix', ['seconds_of_day', 'latitude', 'longitude', 'altitude', 'enl'])


def flight_path(path, max_points=1000):
    f = os.popen('./FlightPath' + ' --max-points=' + str(max_points) + ' "' + path + '"')

    path = []
    for line in f:
        line = line.split()
        path.append(FlightPathFix(int(line[0]), float(line[1]), float(line[2]), int(line[3]), int(line[4])))
    return path


def get_flight_path(flight, threshold=0.001, max_points=3000):
    fp = flight_path(flight, max_points)

    num_levels = 4
    zoom_factor = 4
    zoom_levels = [0]
    zoom_levels.extend([round(-math.log(32.0 / 45.0 * (threshold * pow(zoom_factor, num_levels - i - 1)), 2)) for i in range(1, num_levels)])

    max_delta_time = max(4, (fp[-1].seconds_of_day - fp[0].seconds_of_day) / 500)

    encoder = SkyLinesPolyEncoder(num_levels=4, threshold=threshold, zoom_factor=4)

    fixes = map(lambda x: (x.longitude, x.latitude,
                           (x.seconds_of_day / max_delta_time * threshold)), fp)
    fixes = encoder.classify(fixes, remove=False, type="ppd")

    encoded = encoder.encode(fixes['points'], fixes['levels'])

    barogram_t = encoder.encodeList([fp[i].seconds_of_day for i in range(len(fp)) if fixes['levels'][i] != -1])
    barogram_h = encoder.encodeList([fp[i].altitude for i in range(len(fp)) if fixes['levels'][i] != -1])
    enl = encoder.encodeList([fp[i].enl for i in range(len(fp)) if fixes['levels'][i] != -1])

    return encoded

for i in range(0, 100):
    print get_flight_path('31lxpor1.igc')

