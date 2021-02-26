import numpy as np
import rasterio as rio
from tqdm import tqdm

from config import DATA_DIRECTORY, PROC_DATA_DIRECTORY
from src.datasets import load_landcover, load_worldpop, load_viirs
from src.utils import save_array_to_geotiff


output_directory = DATA_DIRECTORY / 'r_model'


for year in tqdm(range(2013, 2020)):
    ntl = load_viirs(year)
    meta = ntl.meta
    ntl_array = ntl.read(1)
    n_rows, n_cols = ntl_array.shape

    rows, cols = np.meshgrid(np.arange(n_rows), np.arange(n_cols), copy=False, indexing='ij')
    lons, lats = ntl.xy(rows.ravel(), cols.ravel())

    # ntl
    ntl_directory = output_directory / 'ntl'
    ntl_directory.mkdir(parents=True, exist_ok=True)
    filename = str(year) + '.tif'
    save_array_to_geotiff(ntl_array, ntl_directory / filename, meta)
    del ntl_array

    # pop
    pop_directory = output_directory / 'pop'
    pop_directory.mkdir(parents=True, exist_ok=True)
    filename = str(year) + '.tif'

    pop = load_worldpop(year)
    pop_array = pop.read(1)
    pop_array = pop_array[pop.index(lons, lats)]
    pop_array[pop_array == -99999] = -32768
    save_array_to_geotiff(pop_array.reshape((n_rows,n_cols)), pop_directory / filename, meta)
    del pop_array

    # lulc
    lulc_directory = output_directory / 'lulc'
    lulc_directory.mkdir(parents=True, exist_ok=True)
    filename = str(year) + '.tif'

    lulc = load_landcover(year)
    lulc_array = lulc.read(1)
    lulc_array = lulc_array[lulc.index(lons, lats)]

    save_array_to_geotiff(lulc_array.reshape((n_rows,n_cols)), lulc_directory / filename, meta)
    del lulc_array

    # pia
    pia_directory = output_directory / 'pia'
    pia_directory.mkdir(parents=True, exist_ok=True)
    filename = str(year) + '.tif'

    pia = rio.open(PROC_DATA_DIRECTORY / 'pia' / filename)
    pia_array = pia.read(1)
    pia_array = pia_array[pia.index(lons, lats)]
    pia_array = pia_array / 296

    save_array_to_geotiff(pia_array.reshape((n_rows,n_cols)), pia_directory / filename, meta)
    del pia_array
