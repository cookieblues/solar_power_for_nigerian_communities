import shutil

import rasterio as rio
from tqdm import tqdm

from config import RAW_DATA_DIRECTORY, PREP_DATA_DIRECTORY
from ._base import fetch_url, dataset_is_fetched, dataset_is_preprocessed,\
    _crop_raster_to_shapefile


def load_landcover(year):
    """TBA

    Parameters
    ----------
    year : int
        TBA.
    
    Returns
    -------
    landcover : DatasetReader object
        TBA.

    Examples
    --------
    >>> nga_landcover = load_landcover(2010)
    >>> nga_landcover.meta
    >>> nga_landcover.read(1)
    """
    if not dataset_is_preprocessed(f'landcover/{year}.tif'):
        _preprocess_landcover(year)

    dataset_path = PREP_DATA_DIRECTORY / f'landcover/{year}.tif'
    landcover = rio.open(dataset_path)
    return landcover


def _fetch_landcover(year):
    NotImplementedError()


def _preprocess_landcover(year):
    """
    """
    # Setup folders to prepare for the dataset.
    output_directory = PREP_DATA_DIRECTORY / 'landcover'
    output_directory.mkdir(parents=True, exist_ok=True)

    dataset_path = RAW_DATA_DIRECTORY / f'landcover/{year}.tif'
    filename = str(year) + '.tif'
    shutil.copy(dataset_path, output_directory / filename)
    _crop_raster_to_shapefile(output_directory / filename)
