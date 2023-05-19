"""Utilities used to support pipeline runs."""

import yaml
import functools
from pathlib import Path
from dotenv import load_dotenv
from joblib import dump


def load_params_file(key=None):
    """Load parameters for Classfiers."""
    param_file = Path(__file__).parent / "../config/parameters.yml"
    params = load_yaml_config(param_file)
    if key is not None:
        params = params[key]
    return params


def load_data_sources():
    """Load the yaml file containing all data sources."""
    data_sources_file = Path(__file__).parent / "../config/data_sources.yml"
    return load_yaml_config(data_sources_file)


def load_secrets():
    """Load secrets as environment variables."""
    env_path = Path(__file__).parent / "../config/secrets.env"
    load_dotenv(dotenv_path=env_path)
    return True


def load_yaml_config(config_file_name):
    """Load the config yaml file and return dictionary."""
    with config_file_name.open() as params_file:
        params = yaml.full_load(params_file)
    return params


def save_output(data_source):
    """Decorator to save output from a function that returns a pandas DataFrame."""
    config = load_params_file()
    save_output_file = config.get("save_intermediate_datasets")

    def inner_save_output(func):
        @functools.wraps(func)
        def wrapper_save_output(*args, **kwargs):
            output = func(*args, **kwargs)
            if save_output_file is True:
                data_sources_file = Path(__file__).parent / "../config/data_sources.yml"
                data_sources = load_yaml_config(data_sources_file)

                data_source_dict = data_sources.get(data_source)
                if data_source_dict is None:
                    raise KeyError(
                        "Cannot find data source - {} - in data_sources.yml".format(
                            data_source
                        )
                    )
                file_name = data_sources.get(data_source)["file_name"]
                folder = data_sources[data_source]["folder"]

                (Path(__file__).parent / "../data/{}/".format(folder)).mkdir(
                    parents=True, exist_ok=True
                )

                path = Path(__file__).parent / "../data/{}/{}".format(folder, file_name)

                if file_name.split(".")[1] == "csv":
                    output.to_csv(path, index=False)
                elif file_name.split(".")[1] == "png":
                    output.save(path)
                elif file_name.split(".")[1] == "pkl":
                    dump(output, path)
            return output

        return wrapper_save_output

    return inner_save_output
