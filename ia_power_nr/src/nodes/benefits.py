import src.nodes.load_data as ld


def load_benefits_matrix(name):
    """
    Load an X matrix by name.

    Parameters
    ----------
    name : str
        Name of the dataset to load. Should exist in data_sources.yml

    Returns
    -------
    data : pd.DataFrame
        Sample Benefits X Criteria matrix.

    """
    data = ld.load_generic_data(name)
    return data
