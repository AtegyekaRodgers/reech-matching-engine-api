from matching_engine.models.MAB import update_agent
from matching_engine.utilities.mongoDB_utility import update_seen_objects


'''
This is the api for sending the result of user interactions from the "home -> reach for" page
'''


def handle_result(result, _id, profile_id):
    """
    Handles result of user interaction on reach_for page
    :param: int {0,1}, result
    :param: ObjectId, _id
    :param: ObjectId, profile_id
    :return: string
    Updates MAB score on the MongoDB. using a simple greedy algorithm.

    result is an integer, element of {0,1}. 0 indicates negative swipe, 1 indicates positive swipe

    """
    collection = 'profiles'  # access users collection from test database

    update_agent(collection, result, profile_id)

    update_seen_objects('opportunities', _id, 'seenProfiles', profile_id)

    return "success"

