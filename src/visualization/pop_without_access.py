import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio as rio

from config import RAW_DATA_DIRECTORY, DATAVIZ_DIRECTORY

# mpl setup
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams.update({'font.size': 14})
#mpl.rcParams['mathtext.fontset'] = 'stix'

fg = mpl.colors.to_rgb("forestgreen")
gold = mpl.colors.to_rgb("gold")
dg = mpl.colors.to_rgb("darkgreen")
orc = mpl.colors.to_rgb("orchid")
gr = mpl.colors.to_rgb("black")
ora = mpl.colors.to_rgb("orange")
red = mpl.colors.to_rgb("red")

cdict3 = {"red":  ((0.0, gr[0], gr[0]),
                   (0.005, dg[0], dg[0]),
                   (0.125, fg[0], fg[0]),
                   (0.25, gold[0], gold[0]),
                   (0.5, ora[0], ora[0]),
                   (1.0, red[0], red[0])),

         "green": ((0.0, gr[1], gr[1]),
                   (0.005, dg[1], dg[1]),
                   (0.125, fg[1], fg[1]),
                   (0.25, gold[1], gold[1]),
                   (0.5, ora[1], ora[1]),
                   (1.0, red[1], red[1])),

         "blue":  ((0.0, gr[2], gr[2]),
                   (0.005, dg[2], dg[2]),
                   (0.125, fg[2], fg[2]),
                   (0.25, gold[2], gold[2]),
                   (0.5, ora[2], ora[2]),
                   (1.0, red[2], red[2])),
         #"alpha": ((0.0, 0.5, 0.5), (1.0, 0.5, 0.5))
        }
mycmp = mpl.colors.LinearSegmentedColormap("mycmp", cdict3)




# Load merged elevation data
worldpop = rio.open('data/without_access.tif').read(1)
downscale_factor = 5
worldpop = worldpop[::downscale_factor, ::downscale_factor].astype(np.float32)

worldpop[worldpop == -99999] = np.nan

# Setup the matplotlib figure.
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111)

# Plot
im = ax.imshow(worldpop, cmap=mycmp, vmin=0, vmax=1020)

# Colorbar
cbaxes = fig.add_axes([0.075, 0.25, 0.02, 0.5]) 
cb = plt.colorbar(im, cax=cbaxes, ticks=[np.nanmin(worldpop), 200, 400, 600, 800, 1000])
cb.set_label('People per pixel (100m x 100m)')
cbaxes.yaxis.set_label_position('left')
cbaxes.yaxis.set_ticks_position('left')
cb.ax.set_yticklabels([0, 200, 400, 600, 800, 1000])

# Define inset area.
x_min = int(worldpop.shape[0]*0.585)
x_max = int(x_min+(500/downscale_factor))
y_min = int(worldpop.shape[1]*0.145)
y_max = int(y_min+(500/downscale_factor))

# Inset axes.
axins = ax.inset_axes([0.65, -0.025, 0.375, 0.375])
axins.imshow(
    worldpop[y_min:y_max, x_min:x_max],
    extent=[x_min, x_max, y_max, y_min],
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
plt.savefig(DATAVIZ_DIRECTORY / 'pop_without_access.pdf', bbox_inches='tight')
plt.show()
