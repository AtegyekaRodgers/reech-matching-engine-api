import pytest
import json
import pandas as pd
import sys
import os
import pymongo
from bson.objectid import ObjectId
from math import radians, cos, sin, asin, sqrt
from flask import Response, abort

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from matching_engine.utilities.utility import distance, df_to_json,num_ads
from matching_engine.utilities.mongoDB_utility import mongodb_connection, filter_location


@pytest.mark.test_distance_utility
def test_distance_utility():
    coord1 = [200, 100]
    coord2 = [3091, 230]
    assert round(distance(coord1, coord2), 10) == round(14472.415287658576, 10)


@pytest.mark.test_df_to_json_utility
def test_df_to_json_utility():
    df = pd.DataFrame()
    response = df_to_json(df)
    assert type(response) is Response
    assert response.status == "204 NO CONTENT"

    df = pd.DataFrame()
    df['_id'] = [ObjectId(), ObjectId(), ObjectId()]
    df['score'] = [1, 2, 0]
    response = df_to_json(df)
    try:
        decoded_response = json.loads(response)
    except ValueError as e:
        print(e)
        assert False

    assert type(decoded_response) is list
    assert len(decoded_response) == len(df)

    for entry in decoded_response:
        assert type(entry) is dict
        assert "_id" in entry.keys()
        assert "score" in entry.keys()
        assert type(entry["_id"]) is str
        try:
            _ = ObjectId(entry["_id"])
        except ValueError as e:
            print(e)
            assert False


@pytest.mark.test_mongodb_connection_utility
def test_mongodb_connection_utility():
    client = mongodb_connection()
    assert type(client) is pymongo.mongo_client.MongoClient


@pytest.mark.test_filter_location
def test_filter_location():
    """
    Testing this error: https://jira.mongodb.org/browse/SERVER-13540
    """
    client = mongodb_connection()
    db = client.ReechDatabase
    collection = db.opportunities
    _id = ObjectId("63c68bca72c279cc10ff1e58")
    coord1 = db.profiles.find_one({"_id": _id}, )['location']['coordinates']

    response = pd.DataFrame(filter_location(_id, include_distance=True))
    assert len(response) > 10
    for index, row in response.iterrows():
        coord2 = row["location"]['coordinates']
        calculated_dist = distance(coord1, coord2)
        returned_dist = row['distance']
        assert calculated_dist - 5 <= returned_dist <= calculated_dist + 5


@pytest.mark.test_num_ads_utility
def test_num_ads_utility():
    assert num_ads(10) == 2
    assert num_ads(1) == 1
    assert num_ads(99) == 19


