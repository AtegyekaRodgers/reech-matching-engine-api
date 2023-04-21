import json
import os
import sys
from numbers import Number

import pandas as pd
import pytest
from bson.objectid import ObjectId

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from matching_engine.launch import app
from matching_engine.utilities.utility import distance as coordinate_distance
from matching_engine.utilities.mongoDB_utility import mongodb_connection
from matching_engine.utilities.utility import num_ads
from matching_engine.utilities.constants import RATE_WINDOW

client = mongodb_connection()
db = client.ReechDatabase  # access test database from client

''' 
Testing file for ML APIs

Reference:
https://circleci.com/blog/testing-flask-framework-with-pytest/#:~:text=Testing%20Flask%20requires%20that%20we,to%20the%20application%20under%20test.
'''


@pytest.mark.test_index_route
def test_index_route():
    response = app.test_client().get('/')

    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'Reech Machine Learning API is running!'


@pytest.mark.test_embed_job_title_utility
def test_embed_job_title_utility():
    with app.test_client() as c:
        response = c.get("/utilities/embed_job_title/")
    assert response.status_code == 400  # Test if 400 is returned when _id is not passed

    with app.test_client() as c:
        response = c.get("/utilities/embed_job_title/", query_string={'jobTitle': "some job title"})
    assert response.status_code == 200
    decoded_response = json.loads(response.data.decode('utf-8'))
    assert isinstance(decoded_response, list)
    for element in decoded_response:
        assert isinstance(element, Number)


@pytest.mark.test_embed_job_description_utility
def test_embed_job_description_utility():
    with app.test_client() as c:
        response = c.get("/utilities/embed_job_description/")
    assert response.status_code == 400  # Test if 400 is returned when _id is not passed

    with app.test_client() as c:
        response = c.get("/utilities/embed_job_description/", query_string={'jobDescription': "some job description"})
    assert response.status_code == 200
    decoded_response = json.loads(response.data.decode('utf-8'))
    assert isinstance(decoded_response, list)
    for element in decoded_response:
        assert isinstance(element, Number)


@pytest.mark.get_request_reach_for
def test_reach_for_fetch():
    collection = db.opportunities
    data_point = collection.find_one()
    _id = data_point['_id']

    with app.test_client() as c:
        response = c.get('/home/reach_for/fetch/')
    assert response.status_code == 400  # Test if 400 is returned when _id is not passed

    with app.test_client() as c:
        response = c.get('/home/reach_for/fetch/', query_string={'_id': "not_an_ObjectID"})
    assert response.status_code == 400  # Test if 400 is returned when incorrect object type is sent as _id

    # generate ObjectId that is not present in db
    unused_id = ObjectId()
    while True:
        if db.opportunities.count_documents({'_id': unused_id}, limit=1) == 0:
            break
        unused_id = ObjectId()
    with app.test_client() as c:
        response = c.get('/home/reach_for/fetch/', query_string={'_id': unused_id})
    assert response.status_code == 400  # Test if 400 is returned when non existent _id is queried


def custom_get_request_reach_for(request):
    _id = ObjectId("6332fc9ffff689cabc0de425")  # this is a good opportunity object for testing
    collection = db.opportunities
    data_point = collection.find_one({"_id": _id})
    seen_ids = data_point['seenProfiles']
    coordinate = data_point['location']['coordinates']
    radius = data_point['radius']
    rate = data_point["rate"]
    qualification = data_point["qualification"]

    with app.test_client() as c:
        response = c.get('/home/reach_for/fetch/', query_string={'_id': _id, 'request': request})

    assert response.status_code == 200

    if response.status_code == 200:
        res = response.data.decode('utf-8')
        res = json.loads(res)
        assert isinstance(res, list)

        df = pd.DataFrame(res)
        assert "_id" in df.keys()
        assert "score" in df.keys()
        assert len(df) == 10

        for returned_id in df['_id']:
            assert returned_id == str(ObjectId(returned_id))
            assert ObjectId(returned_id) not in seen_ids
            doc = db.profiles.find_one({"_id": ObjectId(returned_id)})
            doc_coordinate = doc["location"]["coordinates"]
            assert coordinate_distance(coordinate, doc_coordinate) <= radius + 2  # +2 for some lee-way
            doc_rate = doc["rate"]
            doc_qualification = doc["qualification"]
            assert qualification >= doc_qualification
            assert (1-RATE_WINDOW)*rate <= doc_rate <= (1+RATE_WINDOW)*rate


@pytest.mark.custom_get_request1_reach_for
def test_index_custom1_reach_for():
    request = ''
    custom_get_request_reach_for(request)


@pytest.mark.custom_get_request2_reach_for
def test_index_custom2_reach_for():
    request = 'plumber'
    custom_get_request_reach_for(request)


@pytest.mark.custom_get_request3_reach_for
def test_index_custom3_reach_for():
    request = 'manager'
    custom_get_request_reach_for(request)


@pytest.mark.get_request_be_reached
def test_be_reached_fetch():
    collection = db.profiles
    data_point = collection.find_one()
    _id = data_point['_id']

    with app.test_client() as c:
        response = c.get('/home/be_reached/fetch/')
    assert response.status_code == 400  # Test if 400 is returned when _id is not passed

    with app.test_client() as c:
        response = c.get('/home/be_reached/fetch/', query_string={'_id': "not_an_ObjectID"})
    assert response.status_code == 400  # Test if 400 is returned when incorrect object type is sent as _id

    # generate ObjectId that is not present in db
    unused_id = ObjectId()
    while True:
        if db.profiles.count_documents({'_id': unused_id}, limit=1) == 0:
            break
        unused_id = ObjectId()
    with app.test_client() as c:
        response = c.get('/home/be_reached/fetch/', query_string={'_id': unused_id})
    assert response.status_code == 400  # Test if 400 is returned when non existent _id is queried


def custom_get_request_be_reached(request):
    _id = ObjectId("63c68bca72c279cc10ff1e58")  # this is a good profile objet for testing
    collection = db.profiles
    data_point = collection.find_one({"_id": _id})
    seen_ids = data_point['seenOpportunities']
    coordinate = data_point['location']['coordinates']
    rate = data_point["rate"]
    qualification = data_point["qualification"]

    with app.test_client() as c:
        response = c.get('/home/be_reached/fetch/', query_string={'_id': _id, 'request': request})

    assert response.status_code == 200

    if response.status_code == 200:
        res = response.data.decode('utf-8')
        res = json.loads(res)
        assert isinstance(res, list)

        df = pd.DataFrame(res)
        assert "_id" in df.keys()
        assert "score" in df.keys()
        assert len(df) == 4

        for returned_id in df['_id']:
            assert returned_id == str(ObjectId(returned_id))
            assert ObjectId(returned_id) not in seen_ids
            doc = db.opportunities.find_one({"_id": ObjectId(returned_id)})
            doc_coordinate = doc["location"]["coordinates"]
            doc_rate = doc["rate"]
            doc_qualification = doc["qualification"]
            radius = doc["radius"]
            assert coordinate_distance(coordinate, doc_coordinate) <= radius + 2  # +2 for some lee-way
            assert qualification >= doc_qualification
            assert (1-RATE_WINDOW)*rate <= doc_rate <= (1+RATE_WINDOW)*rate


@pytest.mark.custom_get_request1_be_reached
def test_index_custom1_be_reached():
    request = ''
    custom_get_request_be_reached(request)


@pytest.mark.custom_get_request2_be_reached
def test_index_custom2_be_reached():
    request = 'plumber'
    custom_get_request_be_reached(request)


@pytest.mark.custom_get_request3_be_reached
def test_index_custom3_be_reached():
    request = 'manager'
    custom_get_request_be_reached(request)


@pytest.mark.get_request_bubble
def test_bubble_fetch():
    with app.test_client() as c:
        response = c.get('/bubble/fetch/')
    assert response.status_code == 400  # Test if 400 is returned when _id is not passed

    with app.test_client() as c:
        response = c.get('/bubble/fetch/', query_string={'_id': "not_an_ObjectID"})
    assert response.status_code == 400  # Test if 400 is returned when incorrect object type is sent as _id

    # generate ObjectId that is not present in db
    unused_id = ObjectId()
    while True:
        if db.users.count_documents({'_id': unused_id}, limit=1) == 0:
            break
        unused_id = ObjectId()
    with app.test_client() as c:
        response = c.get('/bubble/fetch/', query_string={'_id': unused_id})
    assert response.status_code == 400  # Test if 400 is returned when non existent _id is queried

    document = db.users.find_one()  # testing random user
    _id = document["_id"]
    with app.test_client() as c:
        response = c.get('/bubble/fetch/', query_string={'_id': _id})

    assert response.status_code == 200 or response.status_code == 204

    _id = "62e2dedd17e03d2ef3484007"  # testing user with many bubbles on feed
    with app.test_client() as c:
        response = c.get('/bubble/fetch/', query_string={'_id': _id})

    assert response.status_code == 200

    res = response.data.decode('utf-8')

    res = json.loads(res)
    assert isinstance(res, list)

    df = pd.DataFrame(res)

    assert "_id" in df.keys()
    assert "score" in df.keys()

    assert len(df) == 10 + 2


def custom_test_bubble_fetch(n):

    _id = "62e2dedd17e03d2ef3484007"  # testing user with many bubbles on feed
    with app.test_client() as c:
        response = c.get('/bubble/fetch/', query_string={'_id': _id,'n':n})

    assert response.status_code == 200

    res = response.data.decode('utf-8')

    res = json.loads(res)
    assert isinstance(res, list)

    df = pd.DataFrame(res)

    assert "_id" in df.keys()
    assert "score" in df.keys()

    assert len(df) == n + num_ads(n)


@pytest.mark.custom_get_request_bubble1
def custom_get_request_bubble_1():
    for n in range(1, 10):
        custom_test_bubble_fetch(n)


@pytest.mark.post_response_reach_for
def test_reach_for_response():
    profile_document = db.profiles.find_one()
    profile_id = profile_document['_id']

    api_path = '/home/reach_for/response/'

    for result in [0, 1]:
        profile_document = db.profiles.find_one({"_id": profile_id})
        prev_n = profile_document['N_views']
        prev_q = float(profile_document['score'])
        R = float(result)
        coefficient = 1.0 if (prev_n == 0) else (1 / float(prev_n))

        _id = db.opportunities.find_one()['_id']

        with app.test_client() as c:
            response = c.get(api_path, query_string={'result': result, 'profile_id': profile_id, '_id': _id})
        assert response.status_code == 200

        # test if N_views is incremented and if seen_ids is updated
        profile_document = db.profiles.find_one({"_id": profile_id})
        new_n = profile_document['N_views']
        new_q = profile_document['score']
        assert new_n == prev_n + 1
        assert new_q == prev_q + coefficient * (R - prev_q)
        assert profile_id in db.opportunities.find_one({"_id": _id})['seenProfiles']

    with app.test_client() as c:
        response = c.get(api_path, query_string={'profile_id': profile_id, '_id': _id})
    assert response.status_code == 400

    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result, '_id': _id})
    assert response.status_code == 400

    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result, 'profile_id': profile_id})
    assert response.status_code == 400

    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': "not a float", 'profile_id': profile_id, '_id': _id})
    assert response.status_code == 400

    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result, 'profile_id': "not an ObjectId", '_id': _id})
    assert response.status_code == 400

    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result, 'profile_id': profile_id, '_id': "not an ObjectId"})
    assert response.status_code == 400

    # generate ObjectId that is not present in db
    unused_id = ObjectId()
    while True:
        if db.opportunities.count_documents({'_id': unused_id}, limit=1) == 0:
            break
        unused_id = ObjectId()
    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result, 'profile_id': profile_id, '_id': unused_id})
    assert response.status_code == 400  # Test if 400 is returned when non existent _id is queried

    # generate ObjectId that is not present in db
    unused_id = ObjectId()
    while True:
        if db.profiles.count_documents({'_id': unused_id}, limit=1) == 0:
            break
        unused_id = ObjectId()
    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result, 'profile_id': unused_id, '_id': _id})
    assert response.status_code == 400  # Test if 400 is returned when non existent _id is queried


@pytest.mark.post_response_be_reached
def test_be_reached_response():
    api_path = '/home/be_reached/response/'

    opportunity_document = db.opportunities.find_one()
    opportunity_id = opportunity_document['_id']

    for result in [0, 1]:
        opportunity_document = db.opportunities.find_one({"_id": opportunity_id})
        prev_n = opportunity_document['N_views']
        prev_q = float(opportunity_document['score'])
        R = float(result)
        coefficient = 1.0 if (prev_n == 0) else (1 / float(prev_n))

        _id = db.profiles.find_one()['_id']

        with app.test_client() as c:
            response = c.get(api_path, query_string={'result': result, 'opportunity_id': opportunity_id, '_id': _id})
        assert response.status_code == 200

        # test if N_views is incremented and if seen_ids is updated
        opportunity_document = db.opportunities.find_one({"_id": opportunity_id})
        new_n = opportunity_document['N_views']
        new_q = opportunity_document['score']
        assert new_n == prev_n + 1
        assert new_q == prev_q + coefficient * (R - prev_q)
        assert opportunity_id in db.profiles.find_one({"_id": _id})['seenOpportunities']

    with app.test_client() as c:
        response = c.get(api_path, query_string={'opportunity_id': opportunity_id, '_id': _id})
    assert response.status_code == 400

    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result, '_id': _id})
    assert response.status_code == 400

    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result, 'opportunity_id': opportunity_id})
    assert response.status_code == 400

    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': "not a float", 'opportunity_id': opportunity_id, '_id': _id})
    assert response.status_code == 400

    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result, 'opportunity_id': "not an ObjectId", '_id': _id})
    assert response.status_code == 400

    with app.test_client() as c:
        response = c.get(api_path,
                         query_string={'result': result, 'opportunity_id': opportunity_id, '_id': "not an ObjectId"})
    assert response.status_code == 400

    # generate ObjectId that is not present in db
    unused_id = ObjectId()
    while True:
        if db.profiles.count_documents({'_id': unused_id}, limit=1) == 0:
            break
        unused_id = ObjectId()
    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result, 'opportunity_id': opportunity_id, '_id': unused_id})
    assert response.status_code == 400  # Test if 400 is returned when non existent _id is queried

    # generate ObjectId that is not present in db
    unused_id = ObjectId()
    while True:
        if db.opportunities.count_documents({'_id': unused_id}, limit=1) == 0:
            break
        unused_id = ObjectId()
    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result, 'opportunity_id': unused_id, '_id': _id})
    assert response.status_code == 400  # Test if 400 is returned when non existent _id is queried


@pytest.mark.post_response_bubble
def test_bubble_response():
    api_path = '/bubble/response/'

    collection = db.fake_bubbles
    bubble_document = collection.find_one()
    _id = bubble_document['_id']

    for result in [0, 1]:
        bubble_document = collection.find_one({"_id": _id})
        prev_n = bubble_document['N_views']
        prev_q = float(bubble_document['score'])
        R = float(result)
        coefficient = 1.0 if (prev_n == 0) else (1 / float(prev_n))

        with app.test_client() as c:
            response = c.get(api_path, query_string={'result': result, '_id': _id})
        assert response.status_code == 200

        # test if N_views is incremented and if seen_ids is updated
        bubble_document = collection.find_one({"_id": _id})
        new_n = bubble_document['N_views']
        new_q = bubble_document['score']
        assert new_n == prev_n + 1
        assert new_q == prev_q + coefficient * (R - prev_q)

    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result})
    assert response.status_code == 400  # Test if 400 is returned when no _id is passed

    with app.test_client() as c:
        response = c.get(api_path, query_string={'_id': _id})
    assert response.status_code == 400  # Test if 400 is returned when no result is passed

    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result, '_id': "not an ObjectId"})
    assert response.status_code == 400  # Test if 400 is returned when non-convertible _id is passed

    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': "not a float", '_id': _id})
    assert response.status_code == 400  # Test if 400 is returned when non-convertible result is passed

    # generate ObjectId that is not present in db
    unused_id = ObjectId()
    while True:
        if db.fake_bubbles.count_documents({'_id': unused_id}, limit=1) == 0:
            break
        unused_id = ObjectId()
    with app.test_client() as c:
        response = c.get(api_path, query_string={'result': result, '_id': unused_id})
    assert response.status_code == 400  # Test if 400 is returned when non existent _id is queried
