
def embed_job_title(query, model):
    """
    Embeds Job Titles as vectors using the provided model
    :param query: (string) Job Title
    :param model: (Object) with encode() attribute, a transformer that embeds text to vectors
    :return: (list of numbers), a vector embedding of the Job Title
    """
    query = "Job Title:" + query
    vector_query = model.encode(query).tolist()
    return vector_query


def embed_job_description(query, model):
    """
    Embeds Job Titles as vectors using the provided model
    :param query: (string) Job Title
    :param model: (Object) with encode() attribute, a transformer that embeds text to vectors
    :return: (list of numbers), a vector embedding of the Job Title
    """
    query = "Job description:" + query
    vector_query = model.encode(query).tolist()
    return vector_query
