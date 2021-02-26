import os
from urllib.request import urlretrieve

import geopandas as gpd
import rasterio as rio
from rasterio.mask import mask

from config import RAW_DATA_DIRECTORY, PREP_DATA_DIRECTORY, NIGERIA_SHAPEFILE


def get_data_directory():
    return DATA_DIRECTORY


def _crop_raster_to_shapefile(rasterpath, shapepath=NIGERIA_SHAPEFILE):
    nga_shape = gpd.read_file(shapepath)['geometry'][0]
    with rio.open(rasterpath) as nga_elevation:
        cropped_raster, cropped_transform = mask(
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
            'height': cropped_raster.shape[1],
            'width': cropped_raster.shape[2],
            'transform': cropped_transform,
            'nodata': -32768
        })

    with rio.open(rasterpath, 'w', **out_meta) as dest:
        dest.write(cropped_raster)


def dataset_is_fetched(dataset):
    """TBA
    
    Parameters
    ----------
    dataset : string
        TBA
    """
    dataset_path = RAW_DATA_DIRECTORY / dataset
    # If the path exists, then the dataset is fetched.
    return dataset_path.exists()


def dataset_is_preprocessed(dataset):
    """TBA

    Parameters
    ----------
    dataset : string
        TBA
    """
    dataset_path = PREP_DATA_DIRECTORY / dataset
    # If the path exists, then the dataset is fetched.
    return dataset_path.exists()


def fetch_data(country, dataset):
    raise NotImplementedError()


def fetch_url(url, destination):
    # Download the file.
    try:
        urlretrieve(url, destination)
    except:
        print(f'{url} could not be fetched.')


def remove_file(path):
    os.remove(path)
    