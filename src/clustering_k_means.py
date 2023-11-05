from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score, davies_bouldin_score


def clustering_k_means(df, columns_clustering, n_clusters=3, label_column_name='label',
                       post_analysis=True, figure_file_path=None, colors_plot=None, metrics=True):
    """
    Perform k-means clustering on a DataFrame using specified columns and optionally conduct post-analysis.

    Args:
        df (pandas.DataFrame): The input DataFrame containing the data to be clustered.
        columns_clustering (list of str): A list of column names in the DataFrame to be used for clustering.
        n_clusters (int, optional): The number of clusters to create. Default is 3.
        label_column_name (str, optional): The name of the column where cluster labels will be added to the DataFrame.
            Default is 'label'.
        post_analysis (bool, optional): Whether to conduct post-analysis and generate density plots. Default is True.
        figure_file_path (str, optional): The file path to save the generated density plot figure.
        colors_plot (list of str, optional): A list of colors for plotting each cluster's density distribution.
        metrics (bool, optional): Whether to compute and return internal evaluation metrics. Default is True.

    Returns:
        pandas.DataFrame: A DataFrame with an additional column containing cluster labels.
        dict or None: A dictionary containing internal evaluation metrics if metrics=True, otherwise None.

    Example:
        >>> data = {
        ...     'feature1': [1.2, 2.5, 3.1, 4.8, 5.2],
        ...     'feature2': [0.9, 1.8, 2.5, 3.7, 4.0]
        ... }
        >>> df = pd.DataFrame(data)
        >>> columns_to_cluster = ['feature1', 'feature2']
        >>> clustered_df, metrics_dict = clustering_k_means(df, columns_to_cluster, n_clusters=2, post_analysis=False)
        >>> print(clustered_df)
           feature1  feature2  label
        0       1.2       0.9      0
        1       2.5       1.8      0
        2       3.1       2.5      0
        3       4.8       3.7      1
        4       5.2       4.0      1
        >>> print(metrics_dict)
        {
            'Silhouette Score': 0.654,
            'Davies-Bouldin Index': 0.529,
            'Inertia': 2.371
        }
    """
    # Obtain dataframe with the variables for clustering
    df_clustering = df[columns_clustering]

    # Standardize data before clustering
    scaler = StandardScaler()
    df_clustering = scaler.fit_transform(df_clustering)

    # Perform k-means clustering for the specified number of clusters
    clustering_kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init="auto").fit(df_clustering)

    # Add cluster labels to the original dataframe
    df[label_column_name] = list(clustering_kmeans.labels_)

    if post_analysis:
        # Plot density distribution for each variable by clustering label

        # Set up the figure and subplots
        # Calculate the number of rows and columns based on the length of columns_clustering
        num_plots = len(columns_clustering)
        num_cols = min(3, num_plots)
        num_rows = -(-num_plots // num_cols)  # Ceiling division to ensure enough rows

        fig, axe = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=(15, 5))
        # Unpack all the axes subplots
        axes = axe.ravel()

        # Generate colors for plotting if not provided
        if colors_plot is None:
            colors_plot = [plt.cm.jet(i / n_clusters) for i in range(n_clusters)]
        else:
            # Check if the length of colors_plot matches the number of clusters
            if len(colors_plot) != n_clusters:
                raise ValueError("The length of colors_plot must be the same as the number of clusters.")


        # Loop through the continuous variables to create plots
        for i, var in enumerate(columns_clustering):
            ax = axes[i]
            for group_label in df[label_column_name].unique():
                group_data = df[df[label_column_name] == group_label]
                group_color = colors_plot[group_label]
                group_data[var].plot(kind='kde', legend=True, ax=ax, label=group_label, color=group_color)

            # Set title and legend for each subplot
            ax.set_title(f'Density Plot of {var}')
            ax.legend()

        # Add overall title
        title_plot = "Clustering post-analysis"
        fig.suptitle(title_plot, fontsize=16)
        # Adjust layout and save the figure if a file path is provided
        if figure_file_path:
            plt.tight_layout()
            plt.savefig(figure_file_path)
        plt.show()

    if metrics:
        # Compute Silhouette Score (a higher score is better)
        silhouette_avg = silhouette_score(df_clustering, df[label_column_name])

        # Compute Davies-Bouldin Index (lower values are better)
        db_index = davies_bouldin_score(df_clustering, df[label_column_name])

        # Compute Inertia (within-cluster sum of squares) (lower values are better)
        inertia = clustering_kmeans.inertia_

        # Create a dictionary with score information
        score = {
            'Type of Score': ['Silhouette Score', 'Davies-Bouldin Index', 'Inertia'],
            'Range of Values': ['[-1, 1]', '[0, Inf)', '[0, Inf)'],
            'Best Value': ['Higher', 'Lower', 'Lower'],
            'Value for the Score': [silhouette_avg, db_index, inertia]
        }

    return df, score








