# Perform second step of the clustering: subclassification of middle and rural
# Analyse the distribution of each variable used for the clustering by output label

import pickle
from src.clustering_k_means import clustering_k_means
import pandas as pd

# User input to obtain whether we are using the census data from uniform or weighted interpolation
user_input = input("Enter 'uniform' or 'weighted' depending on how you want the census data to have been obtained")

# Read pickle file with features and store in a variable
if user_input == 'weighted':
    file_name = "../../outputs/01_weighted_interpolation/data/UK_clustering_3_tier_labels_h8.pkl"
else:
    file_name = "../../outputs/02_uniform_interpolation/data/UK_clustering_3_tier_labels_h7.pkl"
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
name_label_column_3_tier = column_names_labels[0]

####################
# Perform subclustering for middle and rural area
# Cluster hexagons at resolution 8 level labelled as rural in 3 classes
# Cluster hexagons at resolution 8 level labelled as mid in 2 classes
# Variables for the analysis could be change depending on the variables available in the uk_hex_total dataframe
####################

# Rename labels to add labels of subclasses in the correct order
uk_hex_total[name_label_column_3_tier] = uk_hex_total[name_label_column_3_tier].apply(lambda x: 3 if x == 1 else x)

# Select subset of dataframe with instances for rural and middle class
uk_hex_rural = uk_hex_total.loc[uk_hex_total[name_label_column_3_tier] == 3]
uk_hex_middle = uk_hex_total.loc[uk_hex_total[name_label_column_3_tier] == 0]

################
# Sub-clustering for middle class
################
column_names_extra_middle = ['population_density', 'area_residential', 'length_residential', 'length_tertiary']
n_clusters_middle = 2
name_label_column_middle = 'middle_label_subclass'
colors_middle = ['red', 'maroon']
if user_input == 'weighted':
    file_path_middle = '../../outputs/01_weighted_interpolation/figures/middle_sub_clustering_post_analysis.png'
else:
    file_path_middle = '../../outputs/02_uniform_interpolation/figures/middle_sub_clustering_post_analysis.png'


uk_hex_middle, metrics_middle = clustering_k_means(df=uk_hex_middle, columns_clustering=column_names_extra_middle,
                                                   n_clusters=n_clusters_middle, label_column_name=name_label_column_middle,
                                                   post_analysis=True, colors_plot=colors_middle,
                                                   figure_file_path=file_path_middle, metrics=True)

# Select only labels and geometry before merging
uk_hex_middle_drop = uk_hex_middle[[name_label_column_middle, 'geojson']]
# Merge with original dataframe
uk_hex_total = uk_hex_total.merge(uk_hex_middle_drop, how='outer', on='geojson')

################
# Sub-clustering for rural class
################
column_names_extra_rural = ['population_density', 'area_residential', 'length_residential', 'length_tertiary']
n_clusters_rural = 3
name_label_column_rural = 'rural_label_subclass'
colors_rural = ['greenyellow', 'forestgreen', 'orange']
if user_input == 'weighted':
    file_path_rural = '../../outputs/01_weighted_interpolation/figures/rural_sub_clustering_post_analysis.png'
else:
    file_path_rural = '../../outputs/02_uniform_interpolation/figures/rural_sub_clustering_post_analysis.png'

uk_hex_rural, metrics_rural = clustering_k_means(df=uk_hex_rural, columns_clustering=column_names_extra_rural,
                                                 n_clusters=n_clusters_rural, label_column_name=name_label_column_rural,
                                                 post_analysis=True, colors_plot=colors_rural,
                                                 figure_file_path=file_path_rural, metrics=True)

# Modify labels of subclassification for rural areas before merging back with the whole dataset
uk_hex_rural[name_label_column_rural] = uk_hex_rural[name_label_column_rural].apply(lambda x: x+3)
# Select only labels and geometry before merging
uk_hex_rural_drop = uk_hex_rural[[name_label_column_rural, 'geojson']]
# Merge with original dataframe
uk_hex_total = uk_hex_total.merge(uk_hex_rural_drop, how='outer', on='geojson')


#################
# Combine two-steps from clustering
#################

# Rename column with final two-step clustering labels
n_classes = n_clusters_rural + n_clusters_middle + 1
name_label_column_total = 'label_' + str(n_classes) + '_tier'
uk_hex_total.rename(columns={name_label_column_rural: name_label_column_total}, inplace=True)

# Combine all labels in the same column
uk_hex_total[name_label_column_total] = uk_hex_total[name_label_column_total].\
    fillna(uk_hex_total[name_label_column_middle])  # Incorporate labels from middle subclassification

uk_hex_total[name_label_column_total] = uk_hex_total[name_label_column_total].\
    fillna(uk_hex_total[name_label_column_3_tier])  # Incorporate labels from urban type

# Convert label column to type integer
uk_hex_total[name_label_column_total] = uk_hex_total[name_label_column_total].astype(int)

# Drop column with labels from middle subclassification
uk_hex_total = uk_hex_total.drop(columns=name_label_column_middle)

# Define a dictionary to store scores
scores = {
    '1': {'name': 'Middle Sub-clustering scores', 'scores': metrics_middle},
    '2': {'name': 'Rural Sub-clustering scores', 'scores': metrics_rural}
}

# Print scores based on user input
print("Available Scores:")
print("1. Middle Sub-clustering")
print("2. Rural Sub-clustering")

user_input_results = input("Enter the number(s) of the score(s) you want to print (e.g., '1 2' to print Middle and Rural): ")

selected_score = {key: scores[key] for key in scores if key in user_input_results}

for value in selected_score.values():
    print(value['name'])
    print(pd.DataFrame(data=value['scores']))
    print("\n")

# Save to pickle file
if user_input == 'weighted':
    save_file = '../../outputs/01_weighted_interpolation/data/UK_clustering_labels_h8.pkl'
else:
    save_file = '../../outputs/02_uniform_interpolation/data/UK_clustering_labels_h7.pkl'

uk_hex_total.to_pickle(save_file)

