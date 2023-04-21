# -*- coding: utf-8 -*-

import json
import os
import sys

from bson import ObjectId
from flask import Flask, request, abort
from sentence_transformers import SentenceTransformer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from matching_engine.home_page_APIs.main_reach_for import agent as agent_reach_for
from matching_engine.home_page_APIs.result_reach_for import handle_result as handle_result_reach_for

from matching_engine.home_page_APIs.main_be_reached import agent as agent_be_reached
from matching_engine.home_page_APIs.result_be_reached import handle_result as handle_result_be_reached

from matching_engine.bubble_page_APIs.main import agent as agent_bubble
from matching_engine.bubble_page_APIs.result import handle_result as handle_result_bubble

from matching_engine.utilities.embeddings import embed_job_title, embed_job_description
from matching_engine.utilities.utility import df_to_json
from matching_engine.utilities.mongoDB_utility import mongodb_connection

app = Flask(__name__)

# import the embedding model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

client = mongodb_connection()
db = client.ReechDatabase  # access test database from client


@app.route("/")
def test_index_route():
    """
    Takes no arguments
    http://<local socket>/
    :return: str, response code: 200
    """
    return "Reech Machine Learning API is running!"


@app.route("/utilities/embed_job_title/")
def get_job_title_embedding():
    """
    http://<local socket>/home/reach_for/fetch/?jobTitle=<jobTitle>
    Returns vector embedding of job title as array.

    :param: string, jobTitle being embedded
    :param: int, n
    :return: json list of floats
    """

    job_title = None
    if 'jobTitle' in request.args:
        job_title = request.args['jobTitle']
    else:
        errmsg = '"jobTitle" parameter must be passed'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    embedding = embed_job_title(job_title, model)
    return json.dumps(embedding)  # .JSONEncoder().encode(embedding)


@app.route("/utilities/embed_job_description/")
def get_job_description_embedding():
    """
    http://<local socket>/home/reach_for/fetch/?jobTitle=<jobTitle>
    Returns vector embedding of job title as array.

    :param: string, jobTitle being embedded
    :param: int, n
    :return: json list of floats
    """
    jobDescription = None
    if 'jobDescription' in request.args:
        jobDescription = request.args['jobDescription']
    else:
        errmsg = '"jobDescription" parameter must be passed'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    embedding = embed_job_description(jobDescription, model)
    return json.dumps(embedding)  # .JSONEncoder().encode(embedding)


@app.route("/home/reach_for/fetch/")
def reach_for_fetch():
    """
    http://<local socket>/home/reach_for/fetch/?_id=<_id>&request=<request>&n=<number>
    Returns n home page -> reach for posts in json format.

    :param: string, _id of opportunity reach_for-ing
    :param: string, request
    :param: int, n
    :return: json list of dicts: [{"_id":str,"score":float}],
             response code: 200 or 204 (empty return)
    """
    _id, embedded_job, n = None, None, None
    if '_id' in request.args:
        _id = request.args['_id']
    else:
        errmsg = '"_id" parameter must be passed'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))
    try:
        _id = ObjectId(_id)
    except Exception:
        # Handle the exception
        errmsg = '"_id" must be convertible to ObjectId'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    if db.opportunities.count_documents({'_id': _id}, limit=1) == 0:
        errmsg = '"_id" must be present in opportunities collection'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    if 'request' in request.args:
        requested_job = request.args['request']
    else:
        requested_job = 'general'
    if 'n' in request.args:
        try:
            n = int(request.args['n'])
        except Exception:
            errmsg = '"n" must be convertible to int'
            print(errmsg)
            abort(400, description=json.dumps({"errmsg": errmsg}))
    else:
        n = 10
    embedded_job = embed_job_title(requested_job, model)
    df = agent_reach_for(_id, embedded_job, n)
    return df_to_json(df)


@app.route("/home/reach_for/response/")
def reach_for_response():
    """
    http://<local socket>/home/reach_for/response/?result=<request>&_id=<opportunity_id>&profile_id=<profile_id>
    Updates DB based off of response from user interaction

    :param: int, result {0,1}, 0 if left swipe, 1 if right swipe.
    :param: string, _id, _id of opportunity performing interaction
    :param: string, profile_id, _id of profile interacted with
    :return: response code: 200
    """
    result, _id, profile_id = None, None, None
    #  ========== result ==========
    if 'result' in request.args:
        result = request.args['result']
    else:
        errmsg = '"result" parameter must be passed'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))
    try:
        result = float(result)
    except Exception:
        # Handle the exception
        errmsg = 'result must be convertible to float'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    #  ========== _id ==========

    if '_id' in request.args:
        _id = request.args['_id']
    else:
        errmsg = '"_id" parameter must be passed'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))
    try:
        _id = ObjectId(_id)
    except Exception:
        # Handle the exception
        errmsg = '"_id" must be convertible to ObjectId'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))
    if db.opportunities.count_documents({'_id': _id}, limit=1) == 0:
        errmsg = '"_id" must exist in opportunities collection'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    #  ========== profile_id ==========

    if 'profile_id' in request.args:
        profile_id = request.args['profile_id']
    else:
        errmsg = '"profile_id" parameter must be passed'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))
    try:
        profile_id = ObjectId(profile_id)
    except Exception:
        # Handle the exception
        errmsg = ': must be convertible to ObjectId'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    if db.profiles.count_documents({'_id': profile_id}, limit=1) == 0:
        errmsg = 'profile_id must exist in profiles collection'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    return handle_result_reach_for(result, _id, profile_id)


@app.route("/home/be_reached/fetch/")
def be_reached_fetch():
    """
    http://<local socket>/home/be_reached/fetch/?_id=<_id>&request=<request>&n=<number>
    Returns n home page -> be reached posts in json format.

    :param: string, _id of profile be_reached-ing
    :param: string, request
    :param: int, n
    :return: json list of dicts: [{"_id":str,"score":float}],
             response code: 200 or 204 (empty return)
    """

    _id, embedded_job, n = None, None, None
    if '_id' in request.args:
        _id = request.args['_id']
    else:
        errmsg = '"_id" parameter must be passed'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    try:
        _id = ObjectId(_id)
    except Exception:
        # Handle the exception
        errmsg = '"_id" must be convertible to ObjectId'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    if db.profiles.count_documents({'_id': _id}, limit=1) == 0:
        errmsg = '"_id" must be present in profiles collection'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    if 'request' in request.args:
        requested_job = request.args['request']
    else:
        requested_job = 'manager'
    if 'n' in request.args:
        try:
            n = int(request.args['n'])
        except Exception:
            errmsg = '"n" must be convertible to int'
            print(errmsg)
            abort(400, description=json.dumps({"errmsg": errmsg}))
    else:
        n = 10

    embedded_job = embed_job_title(requested_job, model)
    df = agent_be_reached(_id, embedded_job, n)
    return df_to_json(df)


@app.route("/home/be_reached/response/")
def be_reached_response():
    """
    http://<local socket>/home/reach_for/response/?result=<request>&_id=<_id>&opportunity_id=<opportunity_id>
    Updates DB based off of response from user interaction

    :param: int, result {0,1}, 0 if left swipe, 1 if right swipe.
    :param: string, _id, _id of profile performing interaction
    :param: string, opportunity_id, _id of opportunity interacted with
    :return: response code: 200
    """
    result, _id, opportunity_id = None, None, None
    #  ========== result ==========
    if 'result' in request.args:
        result = request.args['result']
    else:
        errmsg = '"result" parameter must be passed'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))
    try:
        result = float(result)
    except Exception:
        # Handle the exception
        errmsg = 'result must be convertible to float'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    #  ========== _id ==========

    if '_id' in request.args:
        _id = request.args['_id']
    else:
        errmsg = '"_id" parameter must be passed'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))
    try:
        _id = ObjectId(_id)
    except Exception:
        # Handle the exception
        errmsg = '"_id" must be convertible to ObjectId'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))
    if db.profiles.count_documents({'_id': _id}, limit=1) == 0:
        errmsg = '"_id" must be present in profiles collection'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    #  ========== opportunity_id ==========

    if 'opportunity_id' in request.args:
        opportunity_id = request.args['opportunity_id']
    else:
        errmsg = '"opportunity_id" parameter must be passed'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))
    try:
        opportunity_id = ObjectId(opportunity_id)
    except Exception:
        # Handle the exception
        errmsg = '"opportunity_id" must be convertible to ObjectId'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    if db.opportunities.count_documents({'_id': opportunity_id}, limit=1) == 0:
        errmsg = '"opportunity_id" must be present in opportunities collection'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    return handle_result_be_reached(result, _id, opportunity_id)


@app.route("/bubble/fetch/")
def bubble_fetch():
    """
    http://<local socket>/bubble/fetch/?_id=<_id>&n=<number>
    Returns n bubble posts in json format.

    :param: int, n, number of objects to return
    :param: str _id, _id of user
    :return: json list of dicts: [{"_id":str,"score":float}],
             response code: 200 or 204 (empty return). Will be of length n + n//AD_FREQUENCY
    """

    #  ========== _id ==========

    _id, n = None, None
    if '_id' in request.args:
        _id = request.args['_id']
    else:
        errmsg = '"_id" parameter must be passed'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))
    try:
        _id = ObjectId(_id)
    except Exception:
        # Handle the exception
        errmsg = '"_id" must be convertible to ObjectId'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))
    if db.users.count_documents({'_id': _id}, limit=1) == 0:
        errmsg = '"_id" must be present in users collection'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    #  ========== n ==========

    if 'n' in request.args:
        try:
            n = int(request.args['n'])
        except Exception:
            errmsg = '"n" must be convertible to int'
            print(errmsg)
            abort(400, description=json.dumps({"errmsg": errmsg}))
    else:
        n = 10
    df = agent_bubble(_id, n)
    return df_to_json(df)


@app.route("/bubble/response/")
def bubble_response():
    """
    http://<local socket>/home/be_reached/response/?result=<request>&_id=<_id>
    Updates DB based off of response from user interaction

    :param: string, _id of object interacted with
    :param: int, result of interaction. 0 if no interaction, 1 if interacted with
    :return: response code: 200 if successful
                            204 if successful but no more content to show
                            400 if unsuccessful (invalid parameters passed)
    """
    result, _id = None, None
    if 'result' in request.args:
        result = request.args['result']
    else:
        errmsg = '"result" parameter must be passed'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))
    try:
        result = float(result)
    except Exception:
        # Handle the exception
        errmsg = 'result must be convertible to float'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    if '_id' in request.args:
        _id = request.args['_id']
    else:
        errmsg = '"_id" parameter must be passed'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))
    try:
        _id = ObjectId(_id)
    except Exception:
        # Handle the exception
        errmsg = '"_id" must be convertible to ObjectId'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    if db.fake_bubbles.count_documents({'_id': _id}, limit=1) == 0:
        errmsg = '"_id" must be present in bubbles collection'
        print(errmsg)
        abort(400, description=json.dumps({"errmsg": errmsg}))

    return handle_result_bubble(result, _id)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
