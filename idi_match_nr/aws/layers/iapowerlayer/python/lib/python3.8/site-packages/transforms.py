from datetime import date

import re

import pandas as pd

from inspect import getfullargspec

_BOCW_EXPECTED_COLUMNS = [
    "Date of Birth",
    "Gender",
    "Spouse Name",
    "Date of Retirement",
    "Category",
    "Married Status",
    "Period of Membership",
    "Valid Upto/ Next Renewal Date ",
    "Registration No",
]


def _column_check(df, cols):
    """
    check if required columns are present

    Parameters
    ----------
    df : pd.DataFrame
    cols : List[str]
        columns expected

    Raises
    ------
    Exception
        Incorrect columns present
    """
    try:
        df[cols]
        assert _BOCW_EXPECTED_COLUMNS == cols
    except (KeyError, AssertionError):
        raise Exception("Input data does not match expected columns")


def _min_registered_years(date_periods, threshold):
    """
    Compare registered period to integer years

    Parameters
    ----------
    date_periods : List[str]
        String list of date periods
        Data format handled is "X years Y mons Z days"
        "00:00:00" for less than 1 day
    threshold : int
        years for comparison
    """

    def _manipulate_datetime(
        datestring,
    ):
        if "year" in datestring:
            return int(re.match("(\d+) year", datestring)[1])
        else:
            return 0

    return (date_periods.transform(_manipulate_datetime) >= threshold).astype(int)


def _term_match(array_to_search, keyword):
    """
    Search array for existence of keyword

    Parameters
    ----------
    array_to_search : pd.Series
    keyword : str
        case sensitive regex string

    Returns
    -------
    pd.Series
        1 if keyword found else 0 for each cell in array_to_search
    """
    return array_to_search.transform(lambda x: re.search(keyword, x)).transform(
        lambda x: (0, 1)[x is not None]
    )


def _get_elapsed_years(birthdays, age_threshold):
    """
    check if age passes a threshold from dates

    Parameters
    ----------
    birthdays : pd.Series[str]
        column of birth dates (string)
    age_threshold : int
        age of comparison

    Returns
    -------
    pd.Series[int]
        1 if exceeds age threshold else 0
    """
    dates = pd.to_datetime(birthdays)
    present = date.today()
    ages = dates.transform(
        lambda x: present.year
        - x.year
        - ((present.month, present.day) < (x.month, x.day))
    )
    return ages


def _flag_convert(str_flags, key):
    """
    Convert categorical series to binary along key

    Parameters
    ----------
    str_flags : pd.series
        string key values for conversion to binary

    Returns
    -------
    pd.series
        binary version of string flags
    """
    return str_flags.transform(lambda x: (0, 1)[x == key])


def bocw_transform(bocw_raw, columns, target_mapping):
    """
    transform for bocw dataset

    Parameters
    ----------
    bocw_raw : pd.DataFrame
    columns : List[str]
        List of columns
    target_mapping : List[dict]
        List of mapping dictionaries for columns

    Returns
    -------
    pd.DataFrame
        transformed bocw dataset
    """

    _column_check(bocw_raw, columns)

    new_df = pd.DataFrame()
    new_df["beneficiary_name"] = bocw_raw["Registration No"]
    for mapping in target_mapping:
        col = [x for x in mapping.keys()][0]
        transform_args = [x for x in mapping.values()][0]
        source_col = transform_args["source"]

        if source_col:
            evaluated_function = _TRANSFORM_DICT[transform_args["func"]]
            n_args = len(getfullargspec(evaluated_function))

            if n_args == 1:
                new_col = evaluated_function(bocw_raw[source_col])
            else:
                new_col = evaluated_function(
                    bocw_raw[source_col], transform_args["args"]
                )
        else:
            new_col = 1

        new_df[col] = new_col

    return new_df


_TRANSFORM_DICT = {
    "date_to_age": _get_elapsed_years,
    "period_to_years": _min_registered_years,
    "term_match": _term_match,
    "flag_convert": _flag_convert,
}
