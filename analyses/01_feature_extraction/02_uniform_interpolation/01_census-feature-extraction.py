# Import census data (population density, average age and average household size) at the local authority (for England) and the output area (for Scotland) levels and interpolate at the hexagon res 8 level

import pymongo
import pandas as pd
from tqdm import tqdm
import shapely
import geopandas
from tobler.util import h3fy
from tobler.area_weighted import area_interpolate
from src.geometry_to_h3r7 import geometry_to_h3r7

# Client id for database
client = pymongo.MongoClient("35.179.58.255", 27017)  # When database is stored locally
# Select database name for census data
db = client.gb_nationalstatistics # If using another resolution change to the database name

###############
# Extract information about local authority districts and output areas of interest
###############

# Extract local authority districts for England and Wales
cursor_outputareas_england = db.localauthoritydistricts.find()
docs_outputareas_england = list(cursor_outputareas_england)
df_oa_england = pd.DataFrame(docs_outputareas_england)
df_oa_england = df_oa_england[['code', 'geojson']]

# Extract output areas for Scotland
cursor_outputareas_scotland = client.ScotlandSensusData.outputareas.find()
docs_outputareas_scotland = list(cursor_outputareas_scotland)
df_oa_scotland = pd.DataFrame(docs_outputareas_scotland)
df_oa_scotland = df_oa_scotland[['code', 'geojson']]

# Combine output areas for the whole UK
df_outputareas = pd.concat([df_oa_england, df_oa_scotland], ignore_index=True)

###############
# Data extraction at local authority level (England) and output area (Scotland) level
###############

# Extract population density data
# We use population density at the output area level and perform uniform interpolation
with tqdm(desc="Population density") as pbar_population:
    # Population density data at the output area level
    cursor_populationdensity = db.populationdensity.find()
    docs_populationdensity = list(cursor_populationdensity)
    df_population = pd.DataFrame(docs_populationdensity)
    # Rename column to merge datasets
    df_population = df_population.rename(columns={"geographyCode": "code", "value": "population_density"})

    # Merge geometries with population density data
    df_population = pd.merge(df_population, df_outputareas, on='code', how='inner')

    # Keep only hexagon id and population density to merge with the rest of the data
    df_population = df_population[['code', 'population_density']].drop_duplicates()
    pbar_population.update()

# Extract average household size data
with tqdm(desc="Household size") as pbar_household:
    cursor_householdsize = db.householdsize.find()
    docs_householdsize = list(cursor_householdsize)
    df_householdsize = pd.DataFrame(docs_householdsize)

    # Rename column to merge datasets
    df_householdsize = df_householdsize.rename(columns={"geographyCode": "code"})

    # Merge geometries with population density data
    df_householdsize = pd.merge(df_householdsize, df_outputareas, on='code', how='inner')

    # Calculate average household size using the number of households of each size
    df_householdsize['avg_household_size'] = (df_householdsize['1'] + 2 * df_householdsize['2'] +
                                              3 * df_householdsize['3'] + 4 * df_householdsize['4'] +
                                              5 * df_householdsize['5'] + 6 * df_householdsize['6'] +
                                              7 * df_householdsize['7'] +
                                              8 * df_householdsize['8']) / df_householdsize['total']

    # Keep only hexagon id and avg household size to merge with the rest of the data
    df_householdsize = df_householdsize[['code', 'avg_household_size']].drop_duplicates()
    pbar_household.update()

# Extract average age data
with tqdm(desc="Fetching age") as pbar_age:
    cursor_age = db.age.find()
    docs_age = list(cursor_age)
    df_age = pd.DataFrame(docs_age)

    # Rename column to merge datasets
    df_age = df_age.rename(columns={"geographyCode": "code"})

    # Merge geometries with population density data
    df_age = pd.merge(df_age, df_outputareas, on='code', how='inner')

    # Obtain cumulative sum of age and total number of people to compute avg age
    df_age['cumsum_age'] = df_age['agedUnder1Year'].astype('int64') * 0
    df_age['total'] = df_age['agedUnder1Year'].astype('int64') * 0

    for age in range(99):
        age_column = f'agedUnder{age + 1}Year' if age == 0 else f'aged{age + 1}Years'
        df_age['cumsum_age'] = df_age['cumsum_age'] + df_age[age_column].astype('int64') * (age + 1)
        df_age['total'] = df_age['total'] + df_age[age_column].astype('int64')

    # Calculate average
    df_age['avg'] = df_age['cumsum_age']/df_age['total']

    # Keep only hexagon id and avg age to merge with the rest of the data
    df_avg_age = pd.DataFrame({'code': df_age['code'], 'avg_age': df_age['avg']}).drop_duplicates()
    pbar_age.update()

# Combine the dataframes using the hexagon id
with tqdm(desc="Combining DataFrames") as pbar_combine:
    df_final = pd.merge(df_population, df_householdsize, on='code', how='inner')
    df_final = pd.merge(df_final, df_avg_age, on='code', how='inner')
    df_final = pd.merge(df_final, df_outputareas, on='code', how='inner')
    pbar_combine.update(1)


# Modify geometry to have the right format to transform df to GeoDataFrame
df_final['geojson'] = df_final['geojson'].apply(lambda x: shapely.geometry.shape(x))
gdf_final = geopandas.GeoDataFrame(df_final, geometry='geojson')
gdf_final = gdf_final.set_crs(epsg=4326)

# Generate a hexgrid covering the area of interest
resolution_id = 7
gdf_hex = h3fy(gdf_final, resolution=resolution_id, clip=True)

# Interpolate variables
dc_hex_interpolated = area_interpolate(source_df=gdf_final, target_df=gdf_hex,
                                       intensive_variables=['population_density', 'avg_household_size', 'avg_age'])

# Obtain hexagon id from the geometry of the interpolated dataset
dc_hex_interpolated['index'] = dc_hex_interpolated.apply(geometry_to_h3r7, axis=1)
dc_hex_interpolated['geojson'] = dc_hex_interpolated['geometry']

# Save to pickle file
dc_hex_interpolated.to_pickle('../../../data/filter/uniform_census_features_h7_uk.pkl')

