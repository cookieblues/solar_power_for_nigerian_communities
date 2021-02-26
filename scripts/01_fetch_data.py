from tqdm import tqdm

from src.datasets import load_aod, load_colwv, load_coloz, load_elevation, load_worldpop, load_viirs, load_landcover

# load_elevation()

# for year in range(2003, 2019):
#     load_aod(year)
#     load_colwv(year)
#     load_coloz(year)

for year in range(2000, 2021):
    load_landcover(year)
#     load_worldpop(year)


# for year in range(2012, 2020):
#     load_viirs(year)
