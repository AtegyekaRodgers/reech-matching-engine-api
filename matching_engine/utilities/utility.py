# Python 3 program to calculate Distance Between Two Points on Earth
from math import radians, cos, sin, asin, sqrt
import json
from bson import ObjectId
from flask import Response
from matching_engine.utilities.constants import AD_FREQUENCY


def distance(coord1, coord2):
    """
    Calculates distance between two coordinates
    :param coord1: (array) [longitude, latitude] coordinates on Earth
    :param coord2: (array) [longitude, latitude] coordinates on Earth
    :return: (float): the distance between the two coordinates over the surface of the earth.

    https://stackoverflow.com/questions/16819231/geonear-returns-incorrect-distance#:~:text=The%20default%20datum%20for%20an%20earth%2Dlike%20sphere%20in%20MongoDB%202.4%20is%20WGS84.%20Coordinate%2Daxis%20order%20is%20longitude%2C%20latitude.
    """
    lat1 = coord1[1]
    lon1 = coord1[0]

    lat2 = coord2[1]
    lon2 = coord2[0]
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result
    return c * r


class JSONEncoder(json.JSONEncoder):
    """
    Custom JSONEncoder for MongoDB ObjectId objects
    """
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def df_to_json(df):
    """
    Converts pandas.DataFrame to a json response
    :param df: (pandas.DataFrame)
    :return: json Response object
    """
    if df.empty:
        return Response(status=204)

    data = df.T.to_dict().values()
    data = list(data)
    return JSONEncoder().encode(data)


def num_ads(n):
    return n//AD_FREQUENCY if n//AD_FREQUENCY > 0 else 1




