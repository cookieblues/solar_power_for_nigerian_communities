from pathlib import Path


# Data directories.
DATA_DIRECTORY = Path('data')
RAW_DATA_DIRECTORY = DATA_DIRECTORY / 'raw'
PREP_DATA_DIRECTORY = DATA_DIRECTORY / 'preprocessed'
PROC_DATA_DIRECTORY = DATA_DIRECTORY / 'processed'
PLOT_DATA_DIRECTORY = DATA_DIRECTORY / 'plots'

# Dataviz directory.
DATAVIZ_DIRECTORY = Path('report/figures')

# Special files.
NIGERIA_SHAPEFILE = DATA_DIRECTORY / 'nigeria_shapefile/gadm36_NGA_0.shp'

# DHS.
HR_COLS = ['hv001', 'hv206'] # cluster_number, has_electricity
GEO_COLS = [
    'DHSYEAR', 'DHSCLUST', 'URBAN_RURA', 'LATNUM', 'LONGNUM', 'DATUM', 'geometry'
]

# Elevation.
COUNTRIES = {
    'nigeria': (('N004', 'N013'), ('E002', 'E014'))
    #'nigeria-test': (('N009', 'N010'), ('E012', 'E013'))
}
