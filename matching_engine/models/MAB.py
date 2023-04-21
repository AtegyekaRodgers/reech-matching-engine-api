from matching_engine.utilities.mongoDB_utility import fetch_score_and_n_views, update_score_and_n_views


def greedy_agent(data, n):
    """
    :param: pandas.DataFrame, data, empty or with keys {_id,score}
    :return: pandas.DataFrame, data, empty or with keys {_id,score}, sorted as per agent's discretion

    This agent decides what order to show cards to the user, greedily chooses option with highest score.
    Note that as the scores are optimistically initialised, this is an optimistic greedy agent.
    """

    if data.empty:
        return data
    else:
        top_n = data.sort_values(by="score", ascending=False)[:n]
        top_n = top_n[['_id',
                       'score']]
        return top_n


def incremental_update(q_prev, n, reward):
    """
    Performs incremental update for MAB's Q constant (this is the score field on MongoDB)
    :param q_prev: float, previous Q value
    :param n: int, number of views
    :param reward: {0,1}, reward
    :return: float, updated Q value
    """

    coefficient = 1.0 if (n == 0) else (1 / float(n))
    Q_new = q_prev + coefficient * (reward - q_prev)
    return Q_new


def update_agent(collection, result, object_id):
    """
    Update's agent's learned values: { score (i.e.: the Q-value), N_views} according to learning rule.
    :param collection: string, corresponds to name of collection
    :param result: {0,1}, result of user interactions
    :param object_id: _id of object interacted with
    :return: None
    """

    Q_prev, N_prev = fetch_score_and_n_views(collection, object_id)

    Q_new = incremental_update(Q_prev, N_prev, result)

    N_new = N_prev+1

    update_score_and_n_views(collection, object_id, Q_new, N_new)


