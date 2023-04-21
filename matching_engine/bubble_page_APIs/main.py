# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from matching_engine.utilities.mongoDB_utility import fetch_bubbles, fetch_bubble_ads
from matching_engine.utilities.utility import num_ads


'''
API for home page for users that want to be reached
Returns profile cards
'''


def shuffle_in_ads(data, ads):
    """
    Shuffles in ads as per current policy (evenly spread)
    :param data: pd.Dataframe, bubbles
    :param ads: pd.Dataframe, bubble ads
    :return: pd.Dataframe, bubbles and ads shuffled together
    """

    if len(ads) == 0:
        return data

    start = len(data) // len(ads)
    stop = len(data)+len(ads)

    indexes = np.linspace(start, stop, num=len(ads), dtype=int)

    for i in range(len(indexes)):
        index = indexes[i]
        ad = ads.iloc[[i]]

        data = pd.concat([data.iloc[:index], ad, data.iloc[index:]]).reset_index(drop=True)

    return data


def agent(_id, n):
    """
    :param: ObjectId, _id
    :param: int, n
    :return: pandas.DataFrame, Keys: {_id, score}, length<=n

    This agent decides what bubbles to show to the user, orders according to recency as per return of fetch_data
    The options it is presented with are returned by the fetch_data method
    """
    N_ADS = num_ads(n)
    data = fetch_bubbles(_id, n)
    ads = fetch_bubble_ads(_id, N_ADS)

    data = shuffle_in_ads(data, ads)

    if data.empty:
        return data
    else:
        return data[['_id',
                    'score']]
