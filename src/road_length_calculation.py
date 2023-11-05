from geopy.distance import geodesic


def segment_length(coordinates_element):
    """
    Calculate the total length of a path defined by a sequence of coordinates.

    Args:
        coordinates_element (list of tuples): A list of coordinate tuples representing a path.
            Each tuple should contain two elements: latitude and longitude (in that order).

    Returns:
        float: The total length of the path in meters.

    Example:
        >>> coordinates = [(52.5200, 13.4050), (48.8566, 2.3522), (51.5074, -0.1278)]
        >>> segment_length(coordinates)
        1474317.640126704
    """
    dist = [geodesic(coord1, coord2).m for coord1, coord2 in zip(coordinates_element, coordinates_element[1:])]
    return sum(dist)


def road_length(row, road_type):
    """
    Calculate the total length of road segments of a specific type in a given row.

    Args:
        row (list of dictionaries): A list of dictionaries representing road segments.
            Each dictionary should have the following structure:
            {
                'geometry': {
                    'coordinates': [(latitude1, longitude1), (latitude2, longitude2), ...]
                },
                'properties': {
                    'type': str: The type of the road segment (e.g., 'highway', 'street').
                }
            }
        road_type (str): The specific type of road segments to calculate the length for.

    Returns:
        float: The total length of road segments of the specified type in meters.

    Example:
        >>> road_data = [
        ...     {
        ...         'geometry': {'coordinates': [(52.5200, 13.4050), (48.8566, 2.3522)]},
        ...         'properties': {'type': 'highway'}
        ...     },
        ...     {
        ...         'geometry': {'coordinates': [(51.5074, -0.1278), (40.7128, -74.0060)]},
        ...         'properties': {'type': 'street'}
        ...     },
        ...     {
        ...         'geometry': {'coordinates': [(52.5200, 13.4050), (51.5074, -0.1278)]},
        ...         'properties': {'type': 'highway'}
        ...     }
        ... ]
        >>> road_length(road_data, 'highway')
        2344910.426632572
    """
    individual_length = [segment_length(element['geometry']['coordinates']) for element in row if
                         element['properties']['type'] == road_type]
    return sum(individual_length)
