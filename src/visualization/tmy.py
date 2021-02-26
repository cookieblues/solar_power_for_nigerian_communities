import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio as rio

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



# Setup figure
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111)

years = [2014, 2015]
counter = 0
for year in years:
    for month in range(1, 13):
        path = PROC_DATA_DIRECTORY / 'tmy' / str(year)
        filename = month_to_string(month) + '.tif'
        raster = rio.open(path / filename).read(1)
        downscale_factor = 1
        raster = raster[::downscale_factor, ::downscale_factor].astype(np.float32)
        raster[raster < 0] = np.nan
        if month == 1 and year == 2014:
            tmy = raster
        else:
            tmy += raster
        counter += 1

tmy = tmy/counter

im = ax.imshow(tmy, vmin=400, vmax=725, cmap=mycmp)

ax.set_xticks([])
ax.set_yticks([])


# Colorbar
cbaxes = fig.add_axes([0.075, 0.25, 0.02, 0.5])
ticks = [400, 465, 530, 595, 660, 725]
cb = plt.colorbar(im, cax=cbaxes, ticks=ticks)
cb.set_label('Solar irradiance (W/m$^2$)')
cbaxes.yaxis.set_label_position('left')
cbaxes.yaxis.set_ticks_position('left')
cb.ax.set_yticklabels(ticks)

ax.axis('off')
plt.savefig(DATAVIZ_DIRECTORY / 'tmy.pdf', bbox_inches='tight')
plt.show()