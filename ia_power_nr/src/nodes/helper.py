import numpy as np
import pandas as pd

ret_non_na_series = lambda s1, s2: pd.Series(
    [return_non_na(i, j) for i, j in zip(s1, s2)], index=s1.index
)


def return_non_na(a, b):
    """Return non-na value between two bits, otherwise do simple OR."""
    if np.isnan(a) and np.isnan(b):
        return np.nan
    elif np.isnan(a):
        return b
    elif np.isnan(b):
        return a
    else:
        return np.logical_or(a, b)


def augment_eligibility(beneficiary, impute_ref):
    """
    Use logical impute reference to fill in missing cells.

    Parameters
    ----------
    beneficiary : pd.DataFrame
        Y matrix.
    impute_ref : pd.DataFrame
        Logical rules to use.

    Returns
    -------
    beneficiary_data : pd.DataFrame
        Y matrix with some missings logically imputed.

    """
    beneficiary_data = beneficiary.copy()
    for index, rule in impute_ref.iterrows():
        beneficiary_data = beneficiary_data.apply(
            lambda row: update_value(row, rule), axis=1
        )
    return beneficiary_data


def update_value(row, rule):
    """Update value of a row using the logical rule."""
    if row[rule["source_col"]] == 1:
        if (
            ~np.isnan(row[rule["target_col"]])
            and row[rule["target_col"]] != rule["impute_value"]
        ):
            raise ValueError(
                f"Beneficiary characteristis are logically incorrect. "
                f"Check {rule['source_col']} and {rule['target_col']}"
            )
        row[rule["target_col"]] = rule["impute_value"]
    return row
