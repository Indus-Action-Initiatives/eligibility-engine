"""Data loading functions."""

import pandas as pd
import src.utils as utl
from pathlib import Path


def load_generic_data(data_source_name):
    """Load any dataset using the data_sources.yml name."""
    data_sources = utl.load_data_sources()
    my_data_source_info = data_sources[data_source_name]

    file_name = my_data_source_info["file_name"]
    folder = my_data_source_info["folder"]
    args = my_data_source_info.get("args")
    file_type = file_name.split(".")[1]

    if args is None:
        args = {}

    path = Path(__file__).parent / "../../data/{}/{}".format(folder, file_name)

    if file_type == "csv":
        dataset = pd.read_csv(path, **args)
    elif file_type == "dta":
        dataset = pd.read_stata(path, **args)

    return dataset
