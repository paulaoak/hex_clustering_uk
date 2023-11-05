# Visualize clustering outcome

import pickle
import folium
import datetime
from shapely import Polygon
from tqdm import tqdm
from src.style_folium import style
import geopandas as gpd

# User input to obtain whether we are using the census data from uniform or weighted interpolation
user_input = input("Enter 'uniform' or 'weighted' depending on how you want the census data to have been obtained")

# Read pickle file with final clustering output
if user_input == 'weighted':
    file_name = '../../outputs/01_weighted_interpolation/data/UK_clustering_labels_h8.pkl'
else:
    file_name = '../../outputs/02_uniform_interpolation/data/UK_clustering_labels_h7.pkl'
objects = []
with (open(file_name, "rb")) as openfile:
    while True:
        try:
            objects.append(pickle.load(openfile))
        except EOFError:
            break
uk_hex_total = objects[0]
column_names = list(uk_hex_total.columns.values)
column_names_labels = [name for name in column_names if name.startswith('label')]
# Name of column that contains final classification
name_label_column_total = column_names_labels[1]
# Drop geojson column and only keep geometry column
uk_hex_total.drop(columns=['geojson'], inplace=True)
# Convert dataframe to GeoDataFrame format
uk_hex_total = gpd.GeoDataFrame(uk_hex_total, geometry=uk_hex_total['geometry'])
# Define EPSG Geodetic Parameter
uk_hex_total.crs = {'init': 'epsg:4326'}

# Create folium plot with classification
title_progress_bar = "Folium plot is created using labels from the column " +  name_label_column_total
with tqdm(desc=title_progress_bar) as pbar_folium_plot:

    layer = 'Light_3857'
    key = "M4ACNwQ2vRAGGGT2teFgPtuhLq1YSx4L"
    zxy_path = 'https://api.os.uk/maps/raster/v1/zxy/{}/{{z}}/{{x}}/{{y}}.png?key={}'.format(layer, key)

    # Create a new Folium map
    # Ordnance Survey basemap using the OS Data Hub OS Maps API centred on the boundary centroid location
    # Zoom levels 7 - 16 correspond to the open data zoom scales only
    uk_bbox_coords = [[58.6350001085, 1.68153079591], [58.6350001085, -7.57216793459], [49.959999905, -7.57216793459],
                      [49.959999905, 1.68153079591]]
    loc = list(Polygon(uk_bbox_coords).centroid.coords[0])
    m = folium.Map(location=loc,  # centred geocoordinates
                   zoom_start=10,
                   scrollWheelZoom=False,
                   tiles=zxy_path,
                   attr='Contains OS data © Crown copyright and database right {}'.format(datetime.date.today().year))

    date = datetime.datetime.today()  # Obtain date and time

    # List of colors for the different categories
    colors = ['red', 'maroon', 'dodgerblue', 'greenyellow', 'forestgreen', 'orange']
    # Check that the number of colors is greater or equal than the number of classes
    max_value = uk_hex_total[name_label_column_total].max()
    assert len(colors) > max_value, "Error: The length of the vector is smaller than the number of classes."

    # Add color to each element in the dataframe based on clustering labels
    for i in uk_hex_total.index:
        color_id = uk_hex_total.iloc[i][name_label_column_total]
        uk_hex_total.at[i, 'color'] = colors[color_id]

    # Add data to the plot
    folium.GeoJson(data=uk_hex_total, style_function=style).add_to(m)

    if user_input == 'weighted':
        file_name_folium_plot = "../../outputs/01_weighted_interpolation/figures/uk_cluster_6_tier_plot.html"
    else:
        file_name_folium_plot = "../../outputs/02_uniform_interpolation/figures/uk_cluster_6_tier_plot.html"

    m.save(file_name_folium_plot)

    pbar_folium_plot.update(1)