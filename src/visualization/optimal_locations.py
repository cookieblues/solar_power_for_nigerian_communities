import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio as rio
import fiona
from rasterio.plot import show
from descartes import PolygonPatch
from scipy.signal import fftconvolve

from config import RAW_DATA_DIRECTORY, DATAVIZ_DIRECTORY, NIGERIA_SHAPEFILE
from src.utils import *

gr = mpl.colors.to_rgb("midnightblue")
pl = mpl.colors.to_rgb("thistle")

cdict3 = {"red":  ((0.0, gr[0], gr[0]),
                   (1.0, pl[0], pl[0])),

         "green": ((0.0, gr[1], gr[1]),
                   (1.0, pl[1], pl[1])),

         "blue":  ((0.0, gr[2], gr[2]),
                   (1.0, pl[2], pl[2])),
         #"alpha": ((0.0, 0.5, 0.5), (1.0, 0.5, 0.5))
        }
mycmp = mpl.colors.LinearSegmentedColormap("mycmp", cdict3)

def gaussian_blur(in_array, size):
    # expand in_array to fit edge of kernel
    padded_array = np.pad(in_array, size, 'symmetric')
    # build kernel
    x, y = np.mgrid[-size:size + 1, -size:size + 1]
    g = np.exp(-(x**2 / float(size) + y**2 / float(size)))
    g = (g / g.sum()).astype(in_array.dtype)
    # do the Gaussian blur
    return fftconvolve(padded_array, g, mode='valid')

# mpl setup
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams.update({'font.size': 14})
#mpl.rcParams['mathtext.fontset'] = 'stix'

with fiona.open(NIGERIA_SHAPEFILE, "r") as shapefile:
    features = [feature["geometry"] for feature in shapefile]


# Setup the matplotlib figure.
fig = plt.figure(figsize=(12, 6))



for i in range(2):
    ax = fig.add_subplot(1, 2, int(i+1))


    optim_loc = rio.open('data/optimal_locations.tif')
    optim_array = optim_loc.read(1)
    downscale_factor = 5
    optim_array = optim_array[::downscale_factor, ::downscale_factor].astype(np.float32)
    if i == 0:
        percent = np.percentile(optim_array[optim_array != -99999], 5)
    else:
        percent = np.percentile(optim_array[optim_array != -99999], 75)
    optim_array[optim_array < percent] = -99999
    optim_array = gaussian_blur(optim_array, 50)
    optim_array[optim_array < optim_array.mean()] = np.nan
    save_array_to_geotiff(optim_array, 'data/optimal_locations_blur.tif', optim_loc.meta)
    optim_loc.close()

    optim_loc_blur = rio.open('data/optimal_locations_blur.tif')



    show((optim_loc_blur, 1), ax=ax, cmap=mycmp)

    patches = [PolygonPatch(feature, edgecolor="dimgray", facecolor="none", linewidth=0.5) for feature in features]
    ax.add_collection(mpl.collections.PatchCollection(patches, match_original=True))


    ax.axis('off')
    if i == 0:
        ax.set_title('(a)')
    else:
        ax.set_title('(b)')

plt.savefig(DATAVIZ_DIRECTORY / 'optimal_locations.pdf', bbox_inches='tight')
#plt.show()