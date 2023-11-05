import h3
import shapely

def get_hexagon_geometry_shapely(hex_id):
    """
    Get the geometry of a H3 hexagon given its hexagon ID.

    Parameters:
    - hex_id (str): The H3 hexagon ID.

    Returns:
    - shapely.geometry.Polygon: The geometry of the H3 hexagon in shapely.geometry.shape format.
    """

    h3_boundary = h3.h3_to_geo_boundary(hex_id)
    hex_polygon = shapely.geometry.Polygon(h3_boundary)
    return(hex_polygon)