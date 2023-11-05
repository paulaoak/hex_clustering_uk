# Merge the census and OSM data
import pickle

##################
# Merge the 3 datasets of features
##################

# Read pickle file with census features and store in a variable
file_name = "../../../data/filter/uniform_census_features_h7_uk.pkl"
objects = []
with (open(file_name, "rb")) as openfile:
    while True:
        try:
            objects.append(pickle.load(openfile))
        except EOFError:
            break
uk_hex = objects[0]

# Read pickle file with landuse data and store in a variable
file_name = '../../../data/filter/landuse_features_h7_uk.pkl'
objects = []
with (open(file_name, "rb")) as openfile:
    while True:
        try:
            objects.append(pickle.load(openfile))
        except EOFError:
            break
landuse_uk_hex = objects[0]

# Read pickle file with road data and store in a variable
file_name = "../../../data/filter/road_features_h7_uk.pkl"
objects = []
with (open(file_name, "rb")) as openfile:
    while True:
        try:
            objects.append(pickle.load(openfile))
        except EOFError:
            break
road_uk_hex = objects[0]

# Merge roads and landuse dataframes
uk_osm = road_uk_hex.merge(landuse_uk_hex, how='outer', on='index')

# Replace NaN values with 0
uk_osm.fillna(0, inplace=True)

# Merge OSM data with census data
uk_hex_total = uk_hex.merge(uk_osm, how='left', on='index')
uk_hex_total.fillna(0, inplace=True)

# Save to pickle file
uk_hex_total.to_pickle('../../../data/filter/UK_uniform_merged_features_h7_uk.pkl')