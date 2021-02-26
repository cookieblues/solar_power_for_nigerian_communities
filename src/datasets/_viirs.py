from shutil import unpack_archive, rmtree

import numpy as np
import geopandas as gpd
import rasterio as rio
import ee
from rasterio.mask import mask
from rasterio.merge import merge
from tqdm import tqdm

from config import RAW_DATA_DIRECTORY, PREP_DATA_DIRECTORY, NIGERIA_SHAPEFILE
from ._base import fetch_url, dataset_is_fetched, dataset_is_preprocessed, remove_file,\
    _crop_raster_to_shapefile
from ..utils import month_to_string


def load_viirs(year):
    """Download the ALOS World 3D 30 meters resolution dataset.

    Returns
    -------
    viirs : DatasetReader object
        The raster of the viirs of Nigeria.

    Examples
    --------
    >>> nga_viirs = load_viirs()
    >>> nga_viirs.meta
    {'driver': 'GTiff', 'dtype': 'int16', 'nodata': -32768.0, 'width': 43230, 'heigh
    t': 34639, 'count': 1, 'crs': CRS.from_epsg(4326), 'transform': Affine(0.0002777
    777777777778, 0.0, 2.66833333333333,
       0.0, -0.0002777777777777778, 13.892222222222255)}
    >>> nga_viirs.read(1)
    array([[0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 0, 0],
           ...,
           [0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 0, 0]], dtype=int16)
    """
    if year < 2013:
        print('Year provided not high enough (>2012).')
        return

    # If statement to check if the dataset is already downloaded.
    if not dataset_is_fetched(f'viirs/{year}'):
        _fetch_viirs(year)
    
    if not dataset_is_preprocessed(f'viirs/{year}.tif'):
        _preprocess_viirs(year)
    
    dataset_path = PREP_DATA_DIRECTORY / f'viirs/{year}.tif'
    viirs = rio.open(dataset_path)
    return viirs


def _fetch_viirs(year):
    print('Fetching dataset. This can take a while.')

    # Setup folders to prepare for the dataset.
    output_directory = RAW_DATA_DIRECTORY / 'viirs' / str(year)
    output_directory.mkdir(parents=True, exist_ok=True)

    # Initialize Google Earth Engine
    #ee.Authenticate() # first time
    ee.Initialize()

    # Nigeria
    nga_region = [
        [2, 13],
        [2, 4],
        [14, 4],
        [14, 13]
    ]

    months = [month_to_string(i) for i in range(1, 13)]
    pbar = tqdm(total=len(months)*10*13)
    for month in months:
        month_directory = output_directory / month
        month_directory.mkdir(parents=True, exist_ok=True)
        for latitude in range(4, 14):
            for longitude in range(2, 15):
                cur_region = [
                    [longitude, latitude+1],
                    [longitude, latitude],
                    [longitude+1, latitude],
                    [longitude+1, latitude+1]
                ]
                # Image location
                image = ee.Image(f'NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG/{year}{month}01')

                # URL of average radiance
                url = image.select('avg_rad').getDownloadUrl({
                    'scale': 1000,
                    'crs': 'EPSG:4326',
                    'region': cur_region,
                })

                # Filename and fetch
                filename = month + '_' + str(latitude) + '_' + str(longitude)
                fetch_url(url, month_directory / filename)
                pbar.update(1)
    pbar.close()


def _preprocess_viirs(year):
    print('Preprocessing dataset. This can take a while.')

    # Setup folders to prepare for the dataset.
    raw_directory = RAW_DATA_DIRECTORY / 'viirs' / str(year)
    output_directory = PREP_DATA_DIRECTORY / 'viirs'
    output_directory.mkdir(parents=True, exist_ok=True)

    # List to hold all viirs files.
    months = list(raw_directory.iterdir())
    pbar = tqdm(total=len(months)*10*13)
    for idx, month in enumerate(months):
        region_files = list()
        for region in month.iterdir():
            # Extract the archive.
            unpack_archive(region, output_directory, format='zip')
            filename = str(year) + month.stem + '01.avg_rad.tif'

            region_file = rio.open(output_directory / filename)
            region_files.append(region_file)

            # Remove the extracted file.
            remove_file(str(output_directory / filename))
            pbar.update(1)
        
        # Merge all the GeoTIFFs and remove redundant dimension.
        month_file, merged_transformation = merge(region_files)
        if idx == 0:
            year_file = month_file.squeeze()
        else:
            year_file += month_file.squeeze()

    year_raster = rio.open(
        output_directory / f'{year}.tif',
        'w',
        # Same driver, count, dtype, nodata, and crs as the individual GeoTIFFs.
        driver = region_file.meta['driver'],
        count = region_file.meta['count'],
        dtype = region_file.meta['dtype'],
        nodata = region_file.meta['nodata'],
        crs = region_file.meta['crs'],
        transform = merged_transformation,
        height = year_file.shape[0],
        width = year_file.shape[1]
    )

    # Write the merged array to the file.
    year_raster.write(year_file, 1)
    year_raster.close()
    pbar.close()

    _crop_raster_to_shapefile(output_directory / f'{year}.tif')


def _crop_to_shapefile():
    nga_shape = gpd.read_file(NIGERIA_SHAPEFILE)['geometry'][0]
    not_cropped_path = PREP_DATA_DIRECTORY / 'viirs/alos_aw3d30_not_cropped.tif'
    with rio.open(not_cropped_path) as nga_viirs:
        out_image, out_transform = mask(
            nga_viirs,
            nga_shape,
            all_touched=True,
            nodata=-32768,
            crop=True
        )

        # Adjust parameters
        out_meta = nga_viirs.meta
        out_meta.update({
            'driver': 'GTiff',
            'height': out_image.shape[1],
            'width': out_image.shape[2],
            'transform': out_transform,
            'nodata': -32768
        })

    with rio.open(PREP_DATA_DIRECTORY / 'viirs/alos_aw3d30.tif', 'w', **out_meta) as dest:
        dest.write(out_image)









