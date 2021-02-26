# Solar power for Nigerian communities
This is my bachelor project.

## Environment how to
To work in the environment, do the following:
1. Run `pipenv shell`
2. Run `pipenv install`, which will take a few seconds

If you want to run jupyter notebook or jupyter lab, run `pipenv run jupyter notebook` or `pipenv run jupyter lab`.

If you want to install new packages for the environment, then run `pipenv install nameofpackage`.

## Project structure
```
├── README.md          <- The top-level README for anyone using this project.
├── requirements.txt   <- The requirements file for reproducing the project.
├── data
│   ├── raw            <- The original, immutable data dump.
│   ├── preprocessed   <- Intermediate data that has been transformed.
│   └── processed      <- The final, canonical data sets for modeling.
│
├── docs               <- Documentation of this project.
│   ├── references     <- Data dictionaries, manuals, and all other explanatory materials.
│   └── literature     <- Overview of relevant scientific research.
│
├── models             <- Trained and serialized models, model predictions, or model summaries.
│
├── notebooks          <- Jupyter notebooks.
│   └── 1.0-shr-exploratory-data-analysis.ipynb
│
├── report             <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting.
│
└── src                <- Source code for use in this project.
    ├── __init__.py    <- Makes src a Python module.
    ├── spa.py         <- Python implementation of SG2 algorithm.
    ├── utils.py       <- Scripts of helper functions.
    │
    ├── datasets       <- Scripts to download and load data.
    │   ├── __init__.py
    │   ├── _base.py
    │   ├── _aod_.py
    │   ├── _cloud_cover.py
    │   ├── _coloz.py
    │   ├── _colwv.py
    │   ├── _dhs.py
    │   ├── _elevation.py
    │   ├── _landcover.py
    │   ├── _ntl.py
    │   └── _worldpop.py
    │
    ├── feature_engineering    <- Scripts to turn raw data into features for modeling.
    │   ├── __init__.py
    │   ├── _base.py
    │   ├── _albedo.py
    │   ├── _clear_sky.py
    │   ├── _covariates.py
    │   └── _elevation.py
    │
    ├── scripts        <- Scripts to do everything.
    │
    └── visualization  <- Scripts to create results oriented visualizations.
        ├── displaced_households.py
        ├── nigeria_electrification.py
        └── zoom_plot.py
```
