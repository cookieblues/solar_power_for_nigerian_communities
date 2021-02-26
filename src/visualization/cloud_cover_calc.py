import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio as rio
import geopandas as gpd
from rasterio.plot import show
from rasterio.mask import mask

from config import RAW_DATA_DIRECTORY, PREP_DATA_DIRECTORY, DATAVIZ_DIRECTORY, NIGERIA_SHAPEFILE
from src.datasets import load_albedo, load_cloud_cover
from src.utils import *


# mpl setup
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams.update({'font.size': 12})
#mpl.rcParams['mathtext.fontset'] = 'stix'

# Date
year = 2014
month = 10
day = 10
hour = 12

# Original
orig_path = RAW_DATA_DIRECTORY / 'meteosat'
orig_name = str(year) + month_to_string(month) + day_to_string(day) + str(hour) + '00_2.tif'
orig = rio.open(orig_path / orig_name)

nga_shape = gpd.read_file(NIGERIA_SHAPEFILE)['geometry'][0]
cropped_orig, cropped_transform = mask(
    orig,
    nga_shape,
    all_touched=True,
    nodata=-32768,
    crop=True
)
cropped_orig = cropped_orig.squeeze()
cropped_orig = cropped_orig/255
cropped_orig[cropped_orig == -32768] == np.nan

# Albedo
albedo = load_albedo(year, month, day)
albedo_array = albedo.read(1)
#albedo_array[albedo_array == np.nan] = 0

# Cloud cover
cloud_cover = load_cloud_cover(year, month, day, hour)
cloud_cover_array = cloud_cover.read(1)
#cloud_cover_array[cloud_cover_array == np.nan] = 0

# figure setup
fig = plt.figure(figsize=(4, 12))
min_ = 0
max_ = 1

for i in range(1, 4):
    ax = fig.add_subplot(3, 1, i)

    if i == 1:
        ax.imshow(
            cropped_orig,
            cmap='gray',
            vmin=min_,
            vmax=max_
        )
        ax.set_xlabel('(a) Raw Meteosat-10 image of Nigeria taken\n March 3rd, 2014, at 12 UTC.')
    elif i == 2:
        ax.imshow(
            albedo_array,
            cmap='gray',
            vmin=min_,
            vmax=max_
        )
        ax.set_xlabel('(b) Albedo over Nigeria calculated as an\n average of the last 28 days. Data from\n Meteosat-10.')
    elif i == 3:
        ax.imshow(
            cloud_cover_array,
            cmap='gray',
            vmin=min_,
            vmax=max_
        )
        ax.set_xlabel('(c) Cloud cover over Nigeria calculated as\n the original Meteosat-10 image subtracted\n the albedo.')
    ax.set_xticks([])
    ax.set_yticks([])
#plt.tight_layout()
plt.subplots_adjust(wspace=0.05, hspace=0.1)
plt.savefig(DATAVIZ_DIRECTORY / 'cloud_cover_calc.pdf', bbox_inches='tight')
plt.show()



