import numpy as np
import rasterio as rio
from tqdm import tqdm

from config import PROC_DATA_DIRECTORY
from src.datasets import load_worldpop
from src.utils import *

year = 2019
# elec_map = rio.open(f'data/r_model/electricity/electricity_{year}.tif')
# elec_array = elec_map.read(1)

pop_map = load_worldpop(year)
pop_array = pop_map.read(1)
pop_shape = pop_array.shape


# rows, cols = np.meshgrid(
#     np.arange(pop_shape[0]),
#     np.arange(pop_shape[1]),
#     copy=False,
#     indexing='ij'
# )
# rows = rows.ravel()
# cols = cols.ravel()
# N = len(rows)
# indices = np.zeros((N, 2))

# stepsize = 10000
# for i in tqdm(range(0, N, stepsize)):
#     lon, lat = pop_map.xy(rows[i:i+stepsize], cols[i:i+stepsize])
#     indices[i:i+stepsize] = np.column_stack(elec_map.index(lon, lat))

# elec_array[elec_array < 0] = -99999
# save_array_to_geotiff(elec_array[indices[:,0],indices[:,1]].reshape(pop_shape), 'data/heyo.tif', pop_map.meta)


# elec_map = rio.open('data/r_model/electricity/resized_2019.tif')
# elec_array = elec_map.read(1)
# elec_array[elec_array != -99999] = 1-elec_array[elec_array != -99999]


# without_access = np.full(elec_array.shape, -99999)

# idxs = np.logical_and(pop_array != -99999, elec_array != -99999)

# without_access[idxs] = pop_array[idxs] * elec_array[idxs]
# save_array_to_geotiff(without_access, 'data/without_access.tif', pop_map.meta)



without_access = rio.open('data/without_access.tif')
wa_array = without_access.read(1)

# idxs = np.logical_and(pop_array != -99999, wa_array != -99999)
# prop_without_access = np.full(pop_shape, -99999, dtype=np.float32)
# prop_without_access[idxs] = wa_array[idxs] / pop_array[idxs]

# save_array_to_geotiff(prop_without_access, 'data/prop_without_access.tif', pop_map.meta)

grid = rio.open('data/nigeria_electrical_grid_distances.tif')
grid_array = grid.read(1)
grid_array[grid_array != -99999] = grid_array[grid_array != -99999] * 100 # meters
grid_array[grid_array == 0] = 1

#idxs = np.logical_and(grid_array != -99999, wa_array != -99999)

# people_per_distance = np.full(wa_array.shape, -99999)
# people_per_distance[idxs] = wa_array[idxs] / grid_array[idxs]
# save_array_to_geotiff(people_per_distance, 'data/people_per_distance.tif', pop_map.meta)

# distance_per_people = np.full(wa_array.shape, -99999)
# distance_per_people[idxs] = grid_array[idxs] / wa_array[idxs]
# save_array_to_geotiff(distance_per_people, 'data/distance_per_people.tif', pop_map.meta)

# wa_35kms = np.full(wa_array.shape, -99999)
# idxs = np.logical_and(grid_array != -99999, grid_array >= 35000)
# wa_35kms[idxs] = wa_array[idxs]
# save_array_to_geotiff(wa_35kms, 'data/wa_35kms.tif', pop_map.meta)


# Combining
# years = [2014, 2015]
# counter = 0
# for year in years:
#     for month in range(1, 13):
#         path = PROC_DATA_DIRECTORY / 'tmy' / str(year)
#         filename = month_to_string(month) + '.tif'
#         raster = rio.open(path / filename).read(1)
#         downscale_factor = 1
#         raster = raster[::downscale_factor, ::downscale_factor].astype(np.float32)
#         raster[raster < 0] = np.nan
#         if month == 1 and year == 2014:
#             tmy = raster
#         else:
#             tmy += raster
#         counter += 1

# tmy = tmy/np.nanmax(tmy)
# tmy = np.copy(tmy[:-1,:])
# tmy = np.concatenate([tmy, tmy[:,-3:].reshape(-1, 3)], axis=1)
# tmy[np.isnan(tmy)] = -99999
# save_array_to_geotiff(tmy, 'data/tmy_norm.tif', pop_map.meta)
tmy_norm = rio.open('data/tmy_norm.tif')
tmy_norm_array = tmy_norm.read(1)


wa_35kms = rio.open('data/wa_35kms.tif')
wa_35kms_array = wa_35kms.read(1)
idxs = np.logical_and(grid_array != -99999, wa_35kms_array != -99999)
idxs = np.logical_and(wa_35kms_array != 0, idxs)

wa_35kms_dist_per_people = np.full(wa_35kms_array.shape, -99999, dtype=np.float32)
wa_35kms_dist_per_people[idxs] = grid_array[idxs] / wa_35kms_array[idxs]
idxs = wa_35kms_dist_per_people != -99999
wa_35kms_dist_per_people[idxs] = wa_35kms_dist_per_people[idxs] / wa_35kms_dist_per_people[idxs].max()

final = np.full(wa_35kms_array.shape, -99999, dtype=np.float32)
idxs = np.logical_and(wa_35kms_dist_per_people != -99999, tmy_norm_array != -99999)
final[idxs] = wa_35kms_dist_per_people[idxs] * tmy_norm_array[idxs]

save_array_to_geotiff(final, 'data/optimal_locations.tif', pop_map.meta)


