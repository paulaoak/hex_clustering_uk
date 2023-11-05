import h3

def geometry_to_h3r7(row):
    """
    Convert GeoJSON multipolygon geometry to an H3 hexagon of resolution 7 id.

    Parameters:
    row (pandas.Series): A row from a dataframe containing a 'geometry' column.

    Returns:
    str: The H3 hexagon index.

    Usage Example:
    df['h3_index'] = df.apply(convert_to_h3, axis=1)

    Note:
    Ensure the 'geometry' column contains Shapely Polygon or MultiPolygon objects.
    """

    # Get the centroid of the geometry
    centroid = row['geometry'].centroid
    # Convert centroid coordinates to H3 hexagon index
    h3_index = h3.geo_to_h3(centroid.y, centroid.x, resolution=7)
    return h3_index


