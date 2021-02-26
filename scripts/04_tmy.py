from pathlib import Path

import numpy as np
import rasterio as rio
from numba import njit, jit, prange
from tqdm import tqdm

from config import DATA_DIRECTORY, PROC_DATA_DIRECTORY
from src.utils import *


start_year = 2015
end_year = 2016



months = [i for i in range(1, 13)]
days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
hours = [9, 12]

local_path = Path('/media/hdd1/data/processed/')

for year in range(start_year, end_year):
    print('Averaging', year)
    pbar = tqdm(total=sum(days_per_month)*len(hours))
    for month in months:
        counter = 0
        days = days_per_month[month-1]
        if year % 4 == 0 and month == 2:
            days += 1
        for day in range(1, days+1):
            for hour in hours:
                cur_path = local_path / str(year) / month_to_string(month)
                cur_filename = day_to_string(day) + '_' + hour_to_string(hour) + '.tif'
                cur_raster = rio.open(cur_path / cur_filename)
                if counter == 0:
                    month_avg = cur_raster.read(1)
                else:
                    month_avg += cur_raster.read(1)
                counter += 1
                pbar.update(1)
        avg_path = PROC_DATA_DIRECTORY / 'tmy' / str(year) 
        avg_path.mkdir(parents=True, exist_ok=True)
        avg_filename = month_to_string(month) + '.tif'
        save_array_to_geotiff(
            array = month_avg / counter,
            path = avg_path / avg_filename,
            meta = cur_raster.meta
        )




