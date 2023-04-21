from matching_engine.models.MAB import update_agent
from matching_engine.utilities.mongoDB_utility import update_seen_objects

'''
This is the api for sending the result of user interactions from the "home -> be reached" page
'''


def handle_result(result, _id, opportunity_id):
    """
    Handles result of user interaction on be_reached page
    :param: int {0,1}, result
    :param: ObjectId, _id
    :param: ObjectId, opportunity_id
    :return: string
    """

    collection = 'opportunities'

    update_agent(collection, result, opportunity_id)

    update_seen_objects('profiles', _id, 'seenOpportunities', opportunity_id)

    return "success"
