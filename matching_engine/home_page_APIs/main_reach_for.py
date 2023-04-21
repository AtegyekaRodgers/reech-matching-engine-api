# -*- coding: utf-8 -*-
import pandas as pd
from matching_engine.models.MAB import greedy_agent
from matching_engine.utilities.mongoDB_utility import fetch_data


'''
API for home page for users that are reaching for
Returns opportunity cards
'''


def agent(_id, embedded_query, n):
    """
    :param: ObjectId, _id
    :param: array[float], embedded query
    :param: int, n
    :return: pandas.DataFrame, Keys: {_id, score}, length<=n
    """

    data = fetch_data('home.reach_for', _id, embedded_query, n)
    return greedy_agent(data, n)
