import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio as rio
from rasterio.plot import show

from config import RAW_DATA_DIRECTORY, DATAVIZ_DIRECTORY

# mpl setup
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams.update({'font.size': 14})
mpl.rcParams['mathtext.fontset'] = 'stix'

fg = mpl.colors.to_rgb("forestgreen")
gold = mpl.colors.to_rgb("gold")
dg = mpl.colors.to_rgb("darkgreen")
orc = mpl.colors.to_rgb("orchid")
bl = mpl.colors.to_rgb("midnightblue")
ora = mpl.colors.to_rgb("orange")
whi = mpl.colors.to_rgb("thistle")

cdict3 = {"red":  ((0.0, bl[0], bl[0]),
                   #(0.25, bl[0], bl[0]),
                   (1.0, whi[0], whi[0])),

         "green": ((0.0, bl[1], bl[1]),
                   #(0.25, bl[1], bl[1]),
                   (1.0, whi[1], whi[1])),

         "blue":  ((0.0, bl[2], bl[2]),
                   #(0.25, bl[2], bl[2]),
                   (1.0, whi[2], whi[2])),
         #"alpha": ((0.0, 0.5, 0.5), (1.0, 0.5, 0.5))
        }
mycmp = mpl.colors.LinearSegmentedColormap("mycmp", cdict3)




# Load merged elevation data
elec = rio.open('data/r_model/electricity/electricity_2019.tif').read(1)
downscale_factor = 1
elec = elec[::downscale_factor, ::downscale_factor].astype(np.float32)
elec[elec < 0] = np.nan

# Setup the matplotlib figure.
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111)

# Plot
im = ax.imshow(elec, cmap=mycmp)

# Colorbar
cbaxes = fig.add_axes([0.075, 0.25, 0.02, 0.5]) 
cb = plt.colorbar(im, cax=cbaxes, ticks=[np.nanmin(elec), 0.25, 0.5, 0.75, 1.0])
cb.set_label('Probability of electricity access')
cbaxes.yaxis.set_label_position('left')
cbaxes.yaxis.set_ticks_position('left')
cb.ax.set_yticklabels([0, 0.25, 0.5, 0.75, 1.0])

# Define inset area.
x_min = int(elec.shape[0]*0.565)
x_max = int(x_min+(100/downscale_factor))
y_min = int(elec.shape[1]*0.125)
y_max = int(y_min+(100/downscale_factor))

# Inset axes.
# axins = ax.inset_axes([0.55, -0.29, 0.5, 0.5])
# axins.imshow(
#     elec[y_min:y_max, x_min:x_max],
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
plt.savefig(DATAVIZ_DIRECTORY / 'electricity_access_2019.pdf', bbox_inches='tight')
plt.show()
