import pandas as pd
from google.cloud import bigquery
from src.utils import load_params_file


def create_bq_client(target_proj):
    """
    create BigQuery client
    Parameters
    ----------
    target_proj : str
        GCP project name

    Returns
    -------
    Client object
    """

    return bigquery.Client(project=target_proj)


def submit_queries(client, queries):
    """submit queries to client

    Parameters
    ----------
    client : Google Client
    queries : List[str]
        List of queries to submit

    Returns
    -------
    map
        generator of jobs
    """
    return map(lambda x: client.query(x), queries)


def collect_results(jobs):
    """takes jobs and collect outputs

    Parameters
    ----------
    jobs : map
        Query jobs to collect

    Returns
    -------
    List[pd.DataFrame]
    """
    return list(map(lambda x: x.result().to_dataframe(), jobs))


def load_queries():
    return 0


if __name__ == "__main__":
    params = load_params_file()

    client = create_bq_client(params["bq_project_name"])
    queries = [
        "select * from legacy.squadron_admission_process limit 1",
        "select * from legacy.squadron_allotted_students limit 1",
    ]
    jobs = submit_queries(client, queries)
    outputs = collect_results(jobs)
