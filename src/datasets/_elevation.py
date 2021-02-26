from shutil import unpack_archive, rmtree

import numpy as np
import geopandas as gpd
import rasterio as rio
from rasterio.mask import mask
from rasterio.merge import merge
from tqdm import tqdm

from config import RAW_DATA_DIRECTORY, PREP_DATA_DIRECTORY, NIGERIA_SHAPEFILE
from ._base import fetch_url, dataset_is_fetched, dataset_is_preprocessed
from ..utils import latitude_longitude_grid, latitude_to_string, longitude_to_string


def load_elevation():
    """Download the ALOS World 3D 30 meters resolution dataset.

    Returns
    -------
    elevation : DatasetReader object
        The raster of the elevation of Nigeria.

    Examples
    --------
    >>> nga_elevation = load_elevation()
    >>> nga_elevation.meta
    {'driver': 'GTiff', 'dtype': 'int16', 'nodata': -32768.0, 'width': 43230, 'heigh
    t': 34639, 'count': 1, 'crs': CRS.from_epsg(4326), 'transform': Affine(0.0002777
    777777777778, 0.0, 2.66833333333333,
       0.0, -0.0002777777777777778, 13.892222222222255)}
    >>> nga_elevation.read(1)
    array([[0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 0, 0],
           ...,
           [0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 0, 0],
           [0, 0, 0, ..., 0, 0, 0]], dtype=int16)
    """

    # If statement to check if the dataset is already downloaded.
    if not dataset_is_fetched('elevation'):
        _fetch_elevation()
    
    if not dataset_is_preprocessed('elevation'):
        _preprocess_elevation()
    
    #path = PREP_DATA_DIRECTORY / 'elevation/alos_aw3d30.tif'
    path = PREP_DATA_DIRECTORY / 'elevation/nigeria_elevation.tif'
    elevation = rio.open(path)
    return elevation


def _fetch_elevation():
    print('Fetching dataset. This can take a while.')

    # Setup folders to prepare for the dataset.
    output_directory = RAW_DATA_DIRECTORY / 'elevation'
    output_directory.mkdir(parents=True, exist_ok=True)
    
    # ALOS' ftp server of AW3D30 dataset.
    alos_url = 'ftp://ftp.eorc.jaxa.jp/pub/ALOS/ext1/AW3D30/release_v1903'

    # Fetch each latitude/longitude square from ALOS.
    for lat, lon in tqdm(latitude_longitude_grid('nigeria', as_string=False)):
        # Construct the url.
        name = latitude_to_string(lat) + longitude_to_string(lon) + '.tar.gz'
        lat_path = latitude_to_string(lat // 5 * 5)
        lon_path = longitude_to_string(lon // 5 * 5)
        url = alos_url + '/' + lat_path + lon_path + '/' + name

        # Fetch the latitude/longitude square.
        fetch_url(url, output_directory / name)


def _preprocess_elevation():
    print('Preprocessing dataset. This can take a while.')

    # Setup folders to prepare for the dataset.
    raw_directory = RAW_DATA_DIRECTORY / 'elevation'
    output_directory = PREP_DATA_DIRECTORY / 'elevation'
    output_directory.mkdir(parents=True, exist_ok=True)

    # List to hold all elevation files.
    elevation_files = list()
    for archive in tqdm(list(raw_directory.iterdir())):
        # Extract the archive.
        unpack_archive(archive, output_directory)
        
        folder_name = archive.stem.split('.')[0]
        file_name = folder_name + '_AVE_DSM.tif'
        file_path = output_directory / folder_name / file_name

        # Open the GeoTIFF file.with rasterio.open("RGB.byte.masked.tif", "w", **out_meta) as dest:
        elevation_file = rio.open(file_path)
        elevation_files.append(elevation_file)

        # Remove the extracted folder.
        rmtree(output_directory / folder_name)

    # Merge all the GeoTIFFs and remove redundant dimension.
    merged_file, merged_transformation = merge(elevation_files)
    merged_file = merged_file.squeeze()

    # Create new GeoTIFF file for the merged array.
    elevation = rio.open(
        output_directory / 'alos_aw3d30_not_cropped.tif',
        'w',
        # Same driver, count, dtype, nodata, and crs as the individual GeoTIFFs.
        driver = elevation_file.meta['driver'],
        count = elevation_file.meta['count'],
        dtype = elevation_file.meta['dtype'],
        nodata = elevation_file.meta['nodata'],
        crs = elevation_file.meta['crs'],
        transform = merged_transformation,
        height = merged_file.shape[0],
        width = merged_file.shape[1]
    )

    # Write the merged array to the file.
    elevation.write(merged_file, 1)
    elevation.close()

    _crop_to_shapefile()


def _crop_to_shapefile():
    nga_shape = gpd.read_file(NIGERIA_SHAPEFILE)['geometry'][0]
    not_cropped_path = PREP_DATA_DIRECTORY / 'elevation/alos_aw3d30_not_cropped.tif'
    with rio.open(not_cropped_path) as nga_elevation:
        out_image, out_transform = mask(
            nga_elevation,
            nga_shape,
            all_touched=True,
            nodata=-32768,
            crop=True
        )

        # Adjust parameters
        out_meta = nga_elevation.meta
        out_meta.update({
            'driver': 'GTiff',
            'height': out_image.shape[1],
            'width': out_image.shape[2],
            'transform': out_transform,
            'nodata': -32768
        })

    with rio.open(PREP_DATA_DIRECTORY / 'elevation/alos_aw3d30.tif', 'w', **out_meta) as dest:
        dest.write(out_image)









