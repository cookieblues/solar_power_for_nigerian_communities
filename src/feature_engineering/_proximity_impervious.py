import numpy as np
import rasterio as rio
from numba import njit, jit, prange
from tqdm import tqdm

from config import PROC_DATA_DIRECTORY
from ..datasets import load_landcover
from ..utils import haversine_dist, find_corners


def proximity_impervious_area(year):
    """TBA.
    """
    lulc = load_landcover(year)
    meta = lulc.meta
    lulc = lulc.read(1)
    dists = np.full(lulc.shape, -32768, dtype=np.float32)
    
    # Find impervious and other idxs
    other_idxs = np.argwhere((lulc != -32768) & (lulc != 1))
    impervious_idxs = np.argwhere(lulc == 1)
    
    # Calculate distances
    min_dists = _proximity_impervious_area(impervious_idxs, other_idxs)

    dists[other_idxs[:,0], other_idxs[:,1]] = min_dists
    dists[impervious_idxs[:,0], impervious_idxs[:,1]] = 0
    
    # Save as raster.
    filename = str(year) + '.tif'
    pia_raster = rio.open(
        PROC_DATA_DIRECTORY / 'pia' / filename,
        'w',
        driver='GTiff',
        height=meta['height'],
        width=meta['width'],
        nodata=-32768,
        count=1,
        dtype=np.float32,
        crs=meta['crs'],
        transform=meta['transform']
    )
    pia_raster.write(dists.astype(np.float32), 1)
    pia_raster.close()


@jit(parallel=True, nopython=True)
def _proximity_impervious_area(impervious_idxs, other_idxs):
    """TBA.
    """
    n_other = len(other_idxs)
    n_impervious = len(impervious_idxs)
    min_dists = np.full(other_idxs.shape[0], 0)

    for other in prange(n_other):
        if other % (n_other // 100) == 0:
            print(int(100*other/n_other), 'percent done.')

        cur_dists = np.full(impervious_idxs.shape[0], 0)

        cur_other = other_idxs[other]
        other_x, other_y = cur_other[0], cur_other[1]

        for impervious in range(n_impervious):
            cur_impervious = impervious_idxs[impervious]
            impervious_x, impervious_y = cur_impervious[0], cur_impervious[1]

            cur_dist = np.sqrt((impervious_x-other_x)**2 + (impervious_y-other_y)**2)
            cur_dists[impervious] = cur_dist
        
        min_dists[other] = np.min(cur_dists)
    
    return min_dists



