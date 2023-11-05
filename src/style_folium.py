def style(feature):
    """
    Define the style for a feature in a Folium plot.

    Args:
        feature (dict): A dictionary representing a feature with properties including 'color'.

    Returns:
        dict: A dictionary specifying the style properties, including 'fillColor', 'color', and 'weight'.
    """
    return {
        'fillColor': feature['properties']['color'],
        'color': feature['properties']['color'],
        'weight': 1
    }
