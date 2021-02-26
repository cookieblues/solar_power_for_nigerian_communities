import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio as rio

from config import PROC_DATA_DIRECTORY, DATAVIZ_DIRECTORY
from src.utils import month_to_string


# mpl setup
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams.update({'font.size': 14})
#mpl.rcParams['mathtext.fontset'] = 'stix'

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
fig = plt.figure(figsize=(8, 6))
str_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
year = 2014
for month in range(1, 13):
    ax = fig.add_subplot(3, 4, month)
    for idx, year in enumerate(range(2014, 2016)):
        path = PROC_DATA_DIRECTORY / 'tmy' / str(year)
        filename = month_to_string(month) + '.tif'
        if idx == 0:
            raster = rio.open(path / filename).read(1)
        else:
            raster += rio.open(path / filename).read(1)
    raster = raster / 2

    # Scale
    min_ = 400
    max_ = 740
    downscale_factor = 10
    raster = raster[::downscale_factor, ::downscale_factor].astype(np.float32)
    raster[raster < min_] = np.nan

    im = ax.imshow(raster, vmin=min_, vmax=max_, cmap=mycmp)
    ax.set_xlabel(str_months[month-1])

    ax.set_xticks([])
    ax.set_yticks([])
    if month == 11:
        cbaxes = fig.add_axes([0.075, 0.25, 0.02, 0.5])
        cbar = plt.colorbar(
            im,
            cax=cbaxes,
            orientation='vertical',
            ticks = [400, 485, 570, 655, 740]
        )
        cbar.set_label('Solar irradiance (W/m$^2$)')
        cbar.ax.set_yticklabels([400, 485, 570, 655, 740])
        cbaxes.yaxis.set_label_position('left')
        cbaxes.yaxis.set_ticks_position('left')

plt.subplots_adjust(wspace=0.05, hspace=0.1)
plt.savefig(DATAVIZ_DIRECTORY / 'irr_month_avgs.pdf', bbox_inches='tight')
#plt.show()
