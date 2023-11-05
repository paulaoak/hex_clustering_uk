# Import landuse data at the hexagon resolution 8 level

import pymongo
from pandas import DataFrame

# Client id for database
client = pymongo.MongoClient("35.179.58.255", 27017)
db = client.h3r8data  # If using another resolution change to the database name

############
# Obtain landuse data at resolution 8 from database
############

df_landuse = DataFrame(list(db.landuse.find({})))
df_landuse = df_landuse.drop(columns=['_id', 'geojson'])

# Pivot the DataFrame to create the desired structure
pivot_df = df_landuse.pivot(index='index', columns='type', values='area')

# Reset the index and rename the columns
pivot_df.reset_index(inplace=True)
pivot_df.columns.name = None  # Remove the column name
pivot_df.columns = ['index'] + [f'area_{col}' for col in pivot_df.columns[1:]]

# Fill NaN values with 0 if needed
pivot_df.fillna(0, inplace=True)

# Save to pickle file
pivot_df.to_pickle('../../../data/filter/landuse_features_h8_uk.pkl')