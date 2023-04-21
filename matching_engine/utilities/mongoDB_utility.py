import pymongo
from matching_engine.utilities.constants import CLIENT_STRING, RATE_WINDOW
from flask import abort
import json
import pandas as pd


def mongodb_connection():
    """
    Attempts to connect to the mongo client
    :return: pymongo.MongoClient
    """
    try:
        return pymongo.MongoClient(CLIENT_STRING)
    except pymongo.errors.ConnectionFailure as e:
        errmsg = "Could not connect to server: %s" % e
        print(errmsg)
        abort(503, description=json.dumps({"errmsg": errmsg}))


def fetch_score_and_n_views(collection, object_id):
    """
    Fetches score and N_views from MongoDB collection for object with object_id as _id
    :param collection: string, corresponds to name of mongoDB collection
    :param object_id: bson.ObjectId, _id of object in MongoDB collection
    :return: (float, int)
    """
    client = mongodb_connection()
    db = client.ReechDatabase  # access test database from client
    collection = db[collection]

    data_point = collection.find_one({"_id": object_id})

    score = float(data_point['score'])
    n_views = float(data_point['N_views'])
    return score, n_views


def update_score_and_n_views(collection, object_id, score, n_views):
    client = mongodb_connection()
    db = client.ReechDatabase  # access test database from client
    collection = db[collection]

    collection.update_one(
        {'_id': object_id},
        {"$set": {'N_views': n_views, 'score': score}}
    )


def update_seen_objects(collection, _id, seen_objects, object_id):
    """
    Updates list of seen objects on mongoDB
    :param collection: string, corresponds to name of mongoDB collection
    :param _id: bson.ObjectId, _id of object being updated
    :param seen_objects: string, name of field of list of seen objects
    :param object_id: bson.ObjectId, _id of object being added to list of seen objects
    :return: None
    """
    client = mongodb_connection()
    db = client.ReechDatabase  # access test database from client
    collection = db[collection]

    collection.update_one(
        {'_id': _id},
        {'$push': {seen_objects: object_id}}
    )


def filter_location(_id, include_distance=False):
    """
    This method fetches opportunity cards for which the profile falls within their radius.

    :param: _id: ObjectId, _id of profile making the query
    :param: include_distance, optional (default=False) transformer model with method encode() user to encode the query

    :return: list, either empty or containing a dictionary {"all": list([opportunity_id,opportunity_id, *** ])}
    """
    client = mongodb_connection()
    db = client.ReechDatabase  # access test database from client
    collection = db.opportunities  # access job ads collection from test database

    seen_ids = db.profiles.find_one({"_id": _id}, )['seenOpportunities']
    center = db.profiles.find_one({"_id": _id}, )['location']
    coordinates = center['coordinates']

    # Filtering by within radius using collection's radius field
    # https://stackoverflow.com/questions/48760131/in-mongodb-how-do-i-use-a-field-in-the-document-as-input-to-a-geowithin-cente
    # https://stackoverflow.com/questions/27769348/mongodb-geonear-command-result-distance-in-kilometer/27773636#27773636

    filter_location_pipeline = [
        {"$geoNear": {
            "near": {"type": "Point", "coordinates": coordinates},
            "distanceField": "distance",
            "spherical": "true",
            "distanceMultiplier": 0.001
        }},
        {"$addFields": {"isIn": {"$subtract": ["$distance", "$radius"]}}},
        {"$match": {
            "isIn": {"$lte": 0},
            "_id": {"$nin": seen_ids}
        }}
    ]
    project_stage_basic = [
        {"$group": {"_id": "null", "all": {"$addToSet": "$_id"}}},
        {"$project": {"_id": 0, "all": 1}}
    ]

    project_stage_distance = [
        {"$project": {"_id": 1, "distance": 1, "location": 1}}
    ]

    if include_distance:
        filter_location_pipeline.extend(project_stage_distance)
    else:
        filter_location_pipeline.extend(project_stage_basic)

    filter_location_result = collection.aggregate(filter_location_pipeline)

    acceptable_ids = list(filter_location_result)
    return acceptable_ids


def fetch_data(page, _id, embedded_query, n):
    """
    This method decides what cards are shown to the user.
    Uses MongoDB's search api to find cards most appropriate for the user's request.

    :param: page, string {"home.be_reached","home.reach_for"}, corresponds to name of the page that the request is for
    :param: _id: ObjectId, _id of object making the query
    :param: embedded_query: array, vector embedding of jobTitle of position being queried for
    :param: n, int, number of entries to be returned
    :param: model, transformer model with method encode() user to encode the query

    :return: pd.Dataframe of documents
    """

    client = mongodb_connection()
    db = client.ReechDatabase  # access test database from client

    if page == "home.be_reached":
        collection = db.opportunities
        querier = db.profiles.find_one({"_id": _id})
        acceptable_ids = filter_location(_id)
        if len(acceptable_ids) == 0:  # There are no acceptable ids, nothing for user to view
            return pd.DataFrame(acceptable_ids)  # return empty pd.df, triggers 204 return
        acceptable_ids = acceptable_ids[0]['all']
        match_filter = {
            "_id": {"$in": acceptable_ids},
            "qualification": {"$lte": querier['qualification']}
        }
    elif page == "home.reach_for":
        collection = db.profiles  # access users collection from test database
        querier = db.opportunities.find_one({"_id": _id})
        seen_ids = querier['seenProfiles']
        center = querier['location']
        radius = querier['radius']
        coordinates = center['coordinates']

        match_filter = {
            "_id":
                {"$nin": seen_ids},
            'location':
                {'$geoWithin': {'$centerSphere': [coordinates, radius / 6378.1]}},
            "qualification": {"$gte": querier['qualification']}
        }  # MongoDB expects radius values in radians, 6378.1 is radius of earth in Km.

    else:
        raise Exception("'page' parameter must be one of {'home.be_reached','home.reach_for'}")

    rate = querier['rate']
    match_filter["rate"] = {"$gte": (1-RATE_WINDOW)*rate, "$lte": (1+RATE_WINDOW)*rate}

    k = collection.count_documents({})
    vector_search_step = {"$search": {
        'index': 'vector_index',
        "knnBeta": {
            "vector": embedded_query,
            "path": "jobTitle_embedding",
            "k": k,
        }
    }}

    match_step = {"$match": match_filter}

    projection_step = {'$project': {'_id': 1, 'score': 1, }}
    limit_step = {"$limit": n}

    pipeline = [
        vector_search_step,
        match_step,
        projection_step,
        limit_step
    ]

    result = collection.aggregate(pipeline)

    copy = list(result)  # the data must be copied immediately or else it will be deleted

    data = pd.DataFrame(copy)  # convert to pd.df for ease of access

    return data


def fetch_bubbles(_id, n):
    """
    This method decides what cards are shown to the user.
    Uses MongoDB's api to find bubbles fitting the user's request.
    """
    client = mongodb_connection()
    db = client.ReechDatabase  # access test database from client

    data_point = db.users.find_one({"_id": _id})
    friends = data_point['friends']

    match_step = {'$match': {"userId": {"$in": friends}, "ad": None}}
    sort_step = {"$sort": {"date": -1}}
    project_step = {'$project': {'_id': 1, 'score': 1}}
    limit_step = {"$limit": n}

    pipeline = [
        match_step,
        sort_step,
        project_step,
        limit_step
    ]

    result = db.fake_bubbles.aggregate(pipeline)

    copy = list(result)  # the data must be copied immediately or else it will be deleted

    data = pd.DataFrame(copy)  # convert to pd.df for ease of

    return data


def fetch_bubble_ads(_id, n):
    """
    This method decides what cards are shown to the user.
    Uses MongoDB's api to find bubble ads fitting the user's request.
    """
    client = mongodb_connection()
    db = client.ReechDatabase  # access test database from client

    match_step = {'$match': {"ad": True}}
    sort_step = {"$sort": {"date": -1}}
    project_step = {'$project': {'_id': 1, 'score': 1}}
    limit_step = {"$limit": n}

    pipeline = [
        match_step,
        sort_step,
        project_step,
        limit_step
    ]

    result = db.fake_bubbles.aggregate(pipeline)

    copy = list(result)  # the data must be copied immediately or else it will be deleted

    data = pd.DataFrame(copy)  # convert to pd.df for ease of access

    return data
