import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio as rio
from rasterio.plot import show

from config import PREP_DATA_DIRECTORY, DATAVIZ_DIRECTORY

# mpl setup
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams.update({'font.size': 14})
#mpl.rcParams['mathtext.fontset'] = 'stix'

dg = mpl.colors.to_rgb("darkgreen")
fg = mpl.colors.to_rgb("forestgreen")
gold = mpl.colors.to_rgb("gold")
yel = mpl.colors.to_rgb("yellow")
orr = mpl.colors.to_rgb("darkorange")
mar = mpl.colors.to_rgb("saddlebrown")

cdict3 = {"red":  ((0.0, dg[0], dg[0]),
                   (0.05, fg[0], fg[0]),
                   (0.1, yel[0], yel[0]),
                   (0.2, gold[0], gold[0]),
                   (0.4, orr[0], orr[0]),
                   (1.0, mar[0], mar[0])),

         "green": ((0.0, dg[1], dg[1]),
                   (0.05, fg[1], fg[1]),
                   (0.1, yel[1], yel[1]),
                   (0.2, gold[1], gold[1]),
                   (0.4, orr[1], orr[1]),
                   (1.0, mar[1], mar[1])),

         "blue":  ((0.0, dg[2], dg[2]),
                   (0.05, fg[2], fg[2]),
                   (0.1, yel[2], yel[2]),
                   (0.2, gold[2], gold[2]),
                   (0.4, orr[2], orr[2]),
                   (1.0, mar[2], mar[2])),
         #"alpha": ((0.0, 0.5, 0.5), (1.0, 0.5, 0.5))
        }
mycmp = mpl.colors.LinearSegmentedColormap("mycmp", cdict3)




# Load merged elevation data
nga_elevation = rio.open(PREP_DATA_DIRECTORY / 'elevation/alos_aw3d30.tif').read(1)
downscale_factor = 1
nga_elevation = nga_elevation[::downscale_factor, ::downscale_factor].astype(np.float32)

nga_elevation[nga_elevation == -32768] = np.nan

# Setup the matplotlib figure.
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111)

# Plot
im = ax.imshow(nga_elevation, cmap=mycmp)

# Colorbar
cbaxes = fig.add_axes([0.075, 0.25, 0.02, 0.5]) 
cb = plt.colorbar(im, cax=cbaxes)
cb.set_label('Elevation (meters)')
cbaxes.yaxis.set_label_position('left')
cbaxes.yaxis.set_ticks_position('left')

# Define inset area.
x_min = int(nga_elevation.shape[0]*0.65)
x_max = int(x_min+(300/downscale_factor))
y_min = int(nga_elevation.shape[1]*0.40)
y_max = int(y_min+(300/downscale_factor))

# Inset axes.
axins = ax.inset_axes([0.65, -0.025, 0.375, 0.375])
axins.imshow(
    nga_elevation[y_min:y_max, x_min:x_max],
    extent=[x_min, x_max, y_min, y_max],
    cmap=mycmp
)
ax.indicate_inset_zoom(axins, edgecolor='gray', alpha=0.75)

axins.tick_params(
    axis='both',
    which='both',
    bottom=False,
    labelbottom=False,
    left=False,
    labelleft=False,
)
ax.axis('off')
#plt.tight_layout()
plt.savefig(DATAVIZ_DIRECTORY / 'nga_elevation_zoom.pdf', bbox_inches=mpl.transforms.Bbox(np.array([[-0.2, 0], [7.2, 7.2]])))
#plt.show()
