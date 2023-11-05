# Import road data at the hexagon resolution 8 level

import pymongo
import pandas.io.json
from src.road_length_calculation import road_length

# Client id for database
client = pymongo.MongoClient("35.179.58.255", 27017)
db = client.h3r8data  # If using another resolution change to the database name

############
# Obtain road data at resolution 8 from database
############
df_roads = list(db.roads.find({}))
df_roads = pandas.json_normalize(df_roads)
df_roads = df_roads.drop(columns=['_id', 'geojson.type'])

# Calculate length of residential and tertiary roads in each hexagon
df_roads['length_residential'] = df_roads['geojson.features'].map(lambda x: road_length(x, road_type='residential'))
df_roads['length_tertiary'] = df_roads['geojson.features'].map(lambda x: road_length(x, road_type='tertiary'))

df_roads = df_roads.drop(columns=['geojson.features'])

# Save to pickle file
df_roads.to_pickle('../../../data/filter/road_features_h8_uk.pkl')