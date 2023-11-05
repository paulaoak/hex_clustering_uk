# Import census data (population density, average age and average household size) at the hexagon resolution 8 level

import pymongo
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
import h3
from src.get_hexagon_geometry_shapely import get_hexagon_geometry_shapely


# Client id for database
client = pymongo.MongoClient()  # When database is stored locally
# Select database name for census data
db = client.h3r8data # If using another resolution change to the database name

###############
# Data extraction at the hexagon 8 level
###############

# Extract population density data
# We use population density at the output area level and perform uniform interpolation
with tqdm(desc="Population density") as pbar_population:
    cursor_populationdensity = db.age.find()
    docs_populationdensity = list(cursor_populationdensity)
    df_population = pd.DataFrame(docs_populationdensity)

    # Compute hexagon (res 8) area
    df_population['area_h8'] = df_population['index'].apply(lambda x: h3.cell_area(x))

    # Calculate population density
    df_population['population_density'] = df_population['total'] / df_population['area_h8']

    # Keep only hexagon id and population density to merge with the rest of the data
    df_population = df_population[['index', 'population_density']].drop_duplicates()
    pbar_population.update()

# Extract average household size data
with tqdm(desc="Household size") as pbar_household:
    cursor_householdsize = db.householdsize.find()
    docs_householdsize = list(cursor_householdsize)
    df_householdsize = pd.DataFrame(docs_householdsize)

    # Calculate average household size using the number of households of each size
    df_householdsize['avg_household_size'] = (df_householdsize['1'] + 2 * df_householdsize['2'] +
                                              3 * df_householdsize['3'] + 4 * df_householdsize['4'] +
                                              5 * df_householdsize['5'] + 6 * df_householdsize['6'] +
                                              7 * df_householdsize['7'] +
                                              8 * df_householdsize['8']) / df_householdsize['total']

    # Keep only hexagon id and avg household size to merge with the rest of the data
    df_householdsize = df_householdsize[['index', 'avg_household_size']].drop_duplicates()
    pbar_household.update()

# Extract average age data
with tqdm(desc="Fetching age") as pbar_age:
    cursor_age = db.age.find()
    docs_age = list(cursor_age)
    df_age = pd.DataFrame(docs_age)

    # Obtain cumulative sum of age and total number of people to compute avg age
    df_age['cumsum_age'] = df_age['0'].astype('int64') * 0
    df_age['total_p'] = df_age['0'].astype('int64') * 0

    for age in range(101):
        age_column = f'{age}'
        df_age['cumsum_age'] = df_age['cumsum_age'] + df_age[age_column].astype('int64') * (age + 1)
        df_age['total_p'] = df_age['total_p'] + df_age[age_column].astype('int64')

    # Calculate average
    df_age['avg'] = df_age['cumsum_age']/df_age['total_p']

    # Keep only hexagon id and avg age to merge with the rest of the data
    df_avg_age = pd.DataFrame({'index': df_age['index'], 'avg_age': df_age['avg']}).drop_duplicates()
    pbar_age.update()

# Combine the dataframes using the hexagon id
with tqdm(desc="Combining DataFrames") as pbar_combine:
    df_final = pd.merge(df_population, df_householdsize, on='index', how='inner')
    df_final = pd.merge(df_final, df_avg_age, on='index', how='inner')
    pbar_combine.update(1)

# Add geometry to dataframe
df_final['geojson'] = df_final['index'].apply(lambda x: get_hexagon_geometry_shapely(x))

# Convert dataframe to GeoDataFrame format
gdf_geocode = gpd.GeoDataFrame(df_final, geometry=df_final['geojson'])

# Define EPSG Geodetic Parameter
gdf_geocode.crs = {'init': 'epsg:4326'}

# Save to pickle file
gdf_geocode.to_pickle('../../../data/filter/weighted_census_features_h8_uk.pkl')