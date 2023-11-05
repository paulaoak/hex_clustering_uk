# Perform first step of the clustering: urban-mid-rural
# Analyse the distribution of each variable used for the clustering by output label

import pickle
import pandas as pd

from src.clustering_k_means import clustering_k_means

# User input to obtain whether we are using the census data from uniform or weighted interpolation
user_input = input("Enter 'uniform' or 'weighted' depending on how you want the census data to have been obtained")

# Select pickle file to read features and store features in a variable
if user_input == 'weighted':
    file_name = "../../data/filter/UK_weighted_merged_features_h8_uk.pkl"
else:
    file_name = "../../data/filter/UK_uniform_merged_features_h7_uk.pkl"

objects = []
with (open(file_name, "rb")) as openfile:
    while True:
        try:
            objects.append(pickle.load(openfile))
        except EOFError:
            break
uk_hex_total = objects[0]

##################
# Perform first step of the k-means clustering
# Cluster hexagons at resolution 8 level in rural-mid-urban based on population density, avg and avg household size
# Variables for the analysis could be change depending on the variables available in the uk_hex_total dataframe
##################

# Define parameter values clustering function
column_names_clustering_3_tier = ['population_density', 'avg_age', 'avg_household_size']
n_clusters_uk = 3  # rural-mid-urban classification
name_label_column_3_tier = 'label_3_tier'  # Label column name
colors_3_tier = ['red', 'greenyellow', 'dodgerblue']
if user_input == 'weighted':
    file_path_3_tier = '../../outputs/01_weighted_interpolation/figures/3_tier_post_analysis.png'
else:
    file_path_3_tier = '../../outputs/02_uniform_interpolation/figures/3_tier_post_analysis.png'


uk_hex_total, metrics_3_tier = clustering_k_means(df=uk_hex_total, columns_clustering=column_names_clustering_3_tier,
                                                  n_clusters=n_clusters_uk, label_column_name=name_label_column_3_tier,
                                                  post_analysis=True, colors_plot=colors_3_tier,
                                                  figure_file_path=file_path_3_tier, metrics=True)

print('3 Tier Clustering scores')
print(pd.DataFrame(data=metrics_3_tier))

# Save to pickle file
if user_input == 'weighted':
    save_file = '../../outputs/01_weighted_interpolation/data/UK_clustering_3_tier_labels_h8.pkl'
else:
    save_file = '../../outputs/02_uniform_interpolation/data/UK_clustering_3_tier_labels_h7.pkl'
uk_hex_total.to_pickle(save_file)