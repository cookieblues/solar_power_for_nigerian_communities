import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio as rio
from rasterio.plot import show

from config import RAW_DATA_DIRECTORY, DATAVIZ_DIRECTORY
from src.datasets import load_viirs

# mpl setup
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams.update({'font.size': 14})
mpl.rcParams['mathtext.fontset'] = 'stix'

fg = mpl.colors.to_rgb("forestgreen")
gold = mpl.colors.to_rgb("gold")
dg = mpl.colors.to_rgb("darkgreen")
orc = mpl.colors.to_rgb("orchid")
bl = mpl.colors.to_rgb("navy")
blu = mpl.colors.to_rgb("midnightblue")
gold = mpl.colors.to_rgb("gold")

cdict3 = {"red":  ((0.0, bl[0], bl[0]),
                   (0.35, blu[0], blu[0]),
                   (1.0, gold[0], gold[0])),

         "green": ((0.0, bl[1], bl[1]),
                   (0.35, blu[1], blu[1]),
                   (1.0, gold[1], gold[1])),

         "blue":  ((0.0, bl[2], bl[2]),
                   (0.35, blu[2], blu[2]),
                   (1.0, gold[2], gold[2])),
         #"alpha": ((0.0, 0.5, 0.5), (1.0, 0.5, 0.5))
        }
mycmp = mpl.colors.LinearSegmentedColormap("mycmp", cdict3)




# Load merged elevation data
viirs = load_viirs(2015).read(1)
downscale_factor = 1
viirs = viirs[::downscale_factor, ::downscale_factor].astype(np.float32)
viirs[viirs == -32768] = np.nan
viirs = np.log(viirs)

# Setup the matplotlib figure.
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111)

# Plot
im = ax.imshow(viirs, cmap=mycmp)

# Colorbar
cbaxes = fig.add_axes([0.075, 0.25, 0.02, 0.5]) 
cb = plt.colorbar(im, cax=cbaxes, ticks=[np.nanmin(viirs), -1.15, 2.9, 6.95, np.nanmax(viirs)])
cb.set_label('Log of picoWatts/cm$^2$/sr')
cbaxes.yaxis.set_label_position('left')
cbaxes.yaxis.set_ticks_position('left')
cb.ax.set_yticklabels([-5.2, -1.15, 2.9, 6.95, 11])

# Define inset area.
x_min = int(viirs.shape[0]*0.565)
x_max = int(x_min+(100/downscale_factor))
y_min = int(viirs.shape[1]*0.125)
y_max = int(y_min+(100/downscale_factor))

# Inset axes.
# axins = ax.inset_axes([0.65, -0.025, 0.375, 0.375])
# axins.imshow(
#     viirs[y_min:y_max, x_min:x_max],
#     extent=[x_min, x_max, y_min, y_max],
#     cmap=mycmp
# )
# axins.spines['bottom'].set_color('gray')
# axins.spines['top'].set_color('gray')
# axins.spines['left'].set_color('gray')
# axins.spines['right'].set_color('gray')
# ax.indicate_inset_zoom(axins, edgecolor='gray', alpha=0.75)

# axins.tick_params(
#     axis='both',
#     which='both',
#     bottom=False,
#     labelbottom=False,
#     left=False,
#     labelleft=False,
# )
ax.axis('off')
plt.savefig(DATAVIZ_DIRECTORY / 'viirs_zoom.pdf', bbox_inches='tight')
plt.show()
