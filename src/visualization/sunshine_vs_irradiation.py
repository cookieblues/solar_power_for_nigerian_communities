import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio as rio
from tqdm import tqdm

from config import PROC_DATA_DIRECTORY, DATAVIZ_DIRECTORY
from src.utils import month_to_string


# mpl setup
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams.update({'font.size': 14})
mpl.rcParams['mathtext.fontset'] = 'stix'

dkturq = mpl.colors.to_rgb('darkturquoise')
gold = mpl.colors.to_rgb('gold')
red = mpl.colors.to_rgb('red')
mag = mpl.colors.to_rgb('violet')

cdict3 = {"red":  ((0.0, dkturq[0], dkturq[0]),
                   (0.1, dkturq[0], dkturq[0]),
                   (0.5, gold[0], gold[0]),
                   (0.85, red[0], red[0]),
                   (0.95, mag[0], mag[0]),
                   (1.0, mag[0], mag[0])),

         "green": ((0.0, dkturq[1], dkturq[1]),
                   (0.1, dkturq[1], dkturq[1]),
                   (0.5, gold[1], gold[1]),
                   (0.85, red[1], red[1]),
                   (0.95, mag[1], mag[1]),
                   (1.0, mag[1], mag[1])),

         "blue":  ((0.0, dkturq[2], dkturq[2]),
                   (0.1, dkturq[2], dkturq[2]),
                   (0.5, gold[2], gold[2]),
                   (0.85, red[2], red[2]),
                   (0.95, mag[2], mag[2]),
                   (1.0, mag[2], mag[2])),
         #"alpha": ((0.0, 0.5, 0.5), (1.0, 0.5, 0.5))
        }
mycmp = mpl.colors.LinearSegmentedColormap("mycmp", cdict3)


# locations
stations = [
    'Sokoto',
    'Kano',
    'Maiduguri',
    'Jos',
    'Makurdi',
    'Enugu'
]
lats = [
    13+1/60,
    12+3/60,
    11+51/60,
    9+52/60,
    7+42/60,
    6+38/60
]
lons = [
    5+15/60,
    8+32/60,
    13+5/60,
    8+54/60,
    8+35/60,
    7+33/60
]
station_dict = {station: list() for station in stations}


# Setup figure
size = 1
n_stations = len(stations)
fig = plt.figure(figsize=(9, 6))

# years = [2014, 2015]
# for year in years:
#     for month in tqdm(range(1, 13)):
#         path = PROC_DATA_DIRECTORY / 'tmy' / str(year)
#         filename = month_to_string(month) + '.tif'
#         raster = rio.open(path / filename)
#         raster_array = raster.read(1)
#         for i in range(n_stations):
#             cur_station = stations[i]
#             cur_lat, cur_lon = lats[i], lons[i]
#             irradiance = raster_array[raster.index(cur_lon, cur_lat)]
#             station_dict[cur_station].append(irradiance)

# irradiances = {station: list() for station in stations}
# for i in range(n_stations):
#     cur_station = stations[i]
#     cur_station_irrs = station_dict[cur_station]
#     for month in range(12):
#         month_irr = (cur_station_irrs[month] + cur_station_irrs[month+12])/2
#         irradiances[cur_station].append(month_irr)

irradiances = {
    'Sokoto': [617.3832397460938, 652.6962890625, 680.4629516601562, 694.0291748046875, 648.503662109375, 658.6472778320312, 577.6044921875, 546.002197265625, 599.884521484375, 632.519775390625, 626.8292846679688, 633.04345703125],
    'Kano': [641.12255859375, 673.0621337890625, 703.929931640625, 699.2314453125, 647.45751953125, 643.0746459960938, 579.2139892578125, 572.9896240234375, 618.211669921875, 664.002197265625, 629.9641723632812, 652.5368041992188],
    'Maiduguri': [615.682373046875, 669.706298828125, 706.8316650390625, 710.990966796875, 627.358642578125, 623.21728515625, 548.3598022460938, 578.237548828125, 595.8321533203125, 632.8046264648438, 586.4613037109375, 644.5974731445312],
    'Jos': [602.853515625, 665.1016845703125, 689.7857666015625, 688.4427490234375, 619.348388671875, 588.165283203125, 500.47747802734375, 500.1072082519531, 556.11865234375, 628.6873168945312, 555.77197265625, 636.98193359375],
    'Makurdi': [664.516357421875, 666.52587890625, 698.8515625, 704.1702880859375, 615.0689697265625, 585.136962890625, 571.4642333984375, 570.7493896484375, 598.918212890625, 652.2333984375, 662.852783203125, 664.8773193359375],
    'Enugu': [659.541015625, 664.2901611328125, 701.71435546875, 706.8060302734375, 629.8546752929688, 586.4044799804688, 595.9947509765625, 616.4986572265625, 622.6160888671875, 630.8052978515625, 663.6346435546875, 678.0325317382812]
}

sunshine_hours = [
    [279, 269, 282, 255, 279, 282, 229, 198, 243, 307, 279, 298],
    [276, 255, 261, 252, 273, 261, 233, 186, 237, 295, 294, 285],
    [291, 280, 285, 264, 276, 264, 214, 189, 222, 291, 300, 298],
    [307, 274, 260, 220, 208, 201, 152, 127, 171, 242, 294, 313],
    [236, 226, 223, 216, 223, 177, 143, 119, 144, 198, 228, 248],
    [208, 204, 192, 192, 202, 159, 124, 105, 117, 174, 213, 229]
]
from scipy.stats import linregress

for i in range(n_stations):
    ax = fig.add_subplot(2, 3, int(i+1))

    cur_station = stations[i]

    ax.scatter(x=sunshine_hours[i], y=irradiances[cur_station], facecolor='none', edgecolor='midnightblue')

    slope, intercept, rvalue, pvalue, stderr = linregress(sunshine_hours[i], irradiances[cur_station])
    xs = np.linspace(95, 320, num=100)
    ax.plot(xs, intercept + slope*xs, linestyle='--', color='thistle')
    
    ax.set_xlim(95, 320)
    ax.set_ylim(490, 720)
    ax.set_xlabel('Mean sunshine hours')
    ax.set_ylabel('Mean solar irradiance')
    ax.text(310, 500, f'Corr: {rvalue:.2f}', fontsize=12, verticalalignment='center', horizontalalignment='right')

    ax.set_title(stations[i])



#ax.axis('off')
plt.tight_layout()
plt.savefig(DATAVIZ_DIRECTORY / 'sunshine_vs_irradiation.pdf', bbox_inches='tight')
plt.show()