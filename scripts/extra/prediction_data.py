import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import rasterio as rio
from scipy.stats import mode
from tqdm import tqdm

from config import PROC_DATA_DIRECTORY
from src.datasets import load_dhs, load_worldpop, load_landcover, load_viirs
from src.feature_engineering import extract_circle




year = 2019

df = pd.DataFrame(
    columns=['total','LATNUM','LONGNUM','DHSYEAR','pia','ntl','landcover','population']
)

# meters
resolution = 1000
scaler = resolution // 30 # approx resolution of worldpop

pop = load_worldpop(year)
pop_array = pop.read(1)
n_rows, n_cols = pop_array.shape

new_rows = np.arange(int((scaler-1)/2), int(n_rows+1), step=scaler, dtype=np.int32)
new_cols = np.arange(int((scaler-1)/2), int(n_cols+1), step=scaler, dtype=np.int32)

rows, cols = np.meshgrid(new_rows, new_cols, copy=False, indexing='ij')
lons, lats = pop.xy(rows.ravel(), cols.ravel())
df['LONGNUM'] = lons
df['LATNUM'] = lats

df['population'] = pop_array[pop.index(lons, lats)]
del pop_array

lulc = load_landcover(year)
lulc_array = lulc.read(1)
df['landcover'] = lulc_array[lulc.index(lons, lats)]
del lulc_array

ntl = load_viirs(year)
ntl_array = ntl.read(1)
df['ntl'] = ntl_array[ntl.index(lons, lats)]
del ntl_array

filename = str(year) + '.tif'
pia = rio.open(PROC_DATA_DIRECTORY / 'pia' / filename)
pia_array = pia.read(1)
df['pia'] = pia_array[pia.index(lons, lats)]
del pia_array

df['total'] = 1
df['DHSYEAR'] = 2019

df = df.loc[
    (df['population'] != -99999) & \
    (df['pia'] != -32768) & \
    (df['landcover'] != -32768) & \
    (df['ntl'] != -32768)
]
df['pia'] = df['pia'] / 296

df.to_csv('data/r_model/prediction_data.csv', index=False)








