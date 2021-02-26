import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import geopandas as gpd
import geoplot as gplt

from config import DATAVIZ_DIRECTORY, PREP_DATA_DIRECTORY, NIGERIA_SHAPEFILE
from src.datasets import load_dhs


plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams.update({'font.size': 14})
mpl.rcParams['mathtext.fontset'] = 'stix'


gr = mpl.colors.to_rgb("dimgrey")
fg = mpl.colors.to_rgb("forestgreen")
gold = mpl.colors.to_rgb("gold")
dg = mpl.colors.to_rgb("darkgreen")
orc = mpl.colors.to_rgb("orchid")
yel = mpl.colors.to_rgb("yellow")

cdict3 = {"red":  ((0.0, dg[0], dg[0]),
                   (0.33, fg[0], fg[0]),
                   (0.67, gold[0], gold[0]),
                   (1.0, yel[0], yel[0])),

         "green": ((0.0, dg[1], dg[1]),
                   (0.33, fg[1], fg[1]),
                   (0.67, gold[1], gold[1]),
                   (1.0, yel[1], yel[1])),

         "blue":  ((0.0, dg[2], dg[2]),
                   (0.33, fg[2], fg[2]),
                   (0.67, gold[2], gold[2]),
                   (1.0, yel[2], yel[2])),
         #"alpha": ((0.0, 0.5, 0.5), (1.0, 0.5, 0.5))
        }
mycmp = mpl.colors.LinearSegmentedColormap("mycmp", cdict3)


# Load
df = load_dhs()
df = df.loc[df['DHSYEAR'] >= 2013]
df['prop'] = df.has_electricity / df.total

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df['LONGNUM'], df['LATNUM'])
)
nga_shape = gpd.read_file(NIGERIA_SHAPEFILE)

years = sorted(df.DHSYEAR.unique())


# figure setup
fig = plt.figure(figsize=(4, 12))

for i, year in enumerate(years):
    ax = fig.add_subplot(3, 1, int(i+1))

    year_df = gdf.loc[df['DHSYEAR'] == year]
    #test = year_df[['DHSCLUST','geometry']]
    gplt.pointplot(
        year_df,
        hue='prop',
        scale='total',
        edgecolor='lightgray', linewidth=0.25,
        cmap=mycmp,
        legend=True,
        ax=ax
    )
    gplt.polyplot(
        nga_shape,
        ax=ax
    )

    ax.set_title(int(year))

plt.tight_layout()
plt.show()