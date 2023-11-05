## PROJECT. CLUSTERING OF HEXAGONS (H3) IN UK

## Description:
The aim of this project is:

1. To classify the hexagons (H3: Uber’s Hexagonal Hierarchical Spatial Index) of resolution 8 covering the UK into 6 classes that range from totally rural to completely urban.

2. To analyse the performance of the classification in terms of different metrics and visualize the output of the clustering.

It is important to remark that this particular project has been done with data available on 2023-09-05. 

## Organization:
The code and analysis are structured as follows:

## ``` README.md```
This file contains an introduction to the project and how to get started using the project.

## ``` data/```

``` data/filter/```: This folder contains a filtered version of the data comprising landuse features, road length data (both obtained from OSM data) and demographic variables derived from the census data, all of them at the hexagon resolution 8 level. It also includes the combined dataset which merges the three previous files. To change the resolution of the analysis, you need to change the databases from where the data is extracted (more information is included in the description of the analyses folder).

``` data/test/```: This folder contains a test dataset created manually with the categories of different resolution 8 hexagons.

## ``` src/```
This folder contains the source code for functions that are used within the later directories.

- ``` clustering_k_means.py```: perform k-means clustering on a DataFrame using specified columns and optionally conduct post-analysis.

- ```geometry_to_h3r7.py```: convert GeoJSON multipolygon geometry to an H3 hexagon of resolution 7 ID.

- ```get_hexagon_geometry_shapely.py```: get the geometry of a H3 hexagon given its hexagon ID.

- ```road_length_calculation.py```: calculate the total length of road segments of a specific type in a given row.

- ```style_folium.py```: define the style for a feature in a Folium plot.

## ``` analyses/```

### ``` analyses/01_feature_extraction/```:

This folder contains two subdirectories depending on how the census data is obtained, '01_weighted_interpolation' in case census data is interpolated using weights based on the proportion of residential area in each hexagon or '02_uniform_interpolation' if they are obtained using a simple linear normal interpolation.

#### ``` analyses/01_feature_extraction/01_weighted_interpolation/```:

- ```01_census-feature-extraction.py```: compute different features (population density, average age and average household size) from census data at the hexagon 8 resolution level. If another resolution wants to be used the following line of code needs to be changed:

```
# Select database name for census data
db = client.h3res8stats
```

- ```02_osm-landuse-feature-extraction.py```: extract landuse extension of each type at the hexagon resolution 8 level. As before, if the resolution wants to be changed, you need to change the name of the database from where data is extracted.

- ```03_osm-road-feature-extraction.py```: calculate road length of tertiary and residential roads in each hexagon of resolution 8. The resolution can be changed by changing the name of the database that is being used.

- ```04_merge-features.py```: merge census data and osm data from the previous files.

#### ``` analyses/01_feature_extraction/02_uniform_interpolation/```:

- ```01_census-feature-extraction.py```: compute different features (population density, average age and average household size) from census data at the local authority level for England and at the output area level for Scotland and then uniformly interpolates to obtain the values at the hexagon resolution 7 level. If another resolution wants to be used the following line of code needs to be changed:

```
# Generate a hexgrid covering the area of interest
resolution_id = 7
```

The rest of the files mirror that of the other subfolder 'analyses/01_feature_extraction/01_weighted_interpolation/'.

### ``` analyses/02_clustering/```:

- ```01_clustering-first-step-analysis.py```: perform the first step of the clustering dividing the hexagons in three categories: rural, middle and urban. Analysis of the distribution of each variable used for the clustering by output label and calculation of different clustering metrics. The variables used for the algorithm can be changed in the following line of code:
```
# Define parameter values clustering function
column_names_clustering_3_tier = ['population_density', 'avg_age', 'avg_household_size']
```

- ```02_clustering-second-step-analysis.py```: perform the second step of the clustering: subclassification of middle (in 2 subclasses) and rural categories (into 3 categories). Analysis of the distribution of each variable used for the clustering by output label and calculation of different clustering metrics. Like in the previous step of the clustering, the variables used for the k-means algorithm can be modified in the code.

- ```03_clustering-outcome.py```: visualization of results of the clustering algorithm.

## ``` outputs/```
This directory contains the figures and tables with results from the analysis, it is organised in two subfolders depending on how the census data used is computed weighted or uniform interpolation.

#### ``` outputs/01_weighted_interpolated/```:

- ``` outputs/data/```: pickle files of dataframes with census and OSM data and additional columns for the labels obtained in the clustering algorithm.

- ```outputs/figures/```: folium plot to visualize the 6-tier classification.

#### ``` outputs/02_uniform_interpolation/```:
Its structure mirrors that of the other subfolder 'outputs/01_weighted_interpolated/'.

## ``` reports/```
This directory contains the final report of the project in pdf version, the overall workflow of the implementation and the documentation provided by the ONS for the urban-rural classification.
