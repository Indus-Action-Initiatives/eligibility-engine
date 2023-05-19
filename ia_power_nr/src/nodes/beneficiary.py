"""Load and process beneficiary data."""
import pandas as pd
import src.utils as utl
import src.nodes.load_data as ld
import src.nodes.helper as hlp
import numpy as np
import re
import functools as fn


def get_Y_from_bocw(benefits):
    """
    Wrangle pre-transformed BoCW CW registration data into Y matrix.
    Use the pre-processed claims data to add additional eligiblity criteria
    passed.

    Parameters
    ----------
    benefits : pd.DataFrame
        X matrix, benefits and associated eligibility.

    Returns
    -------
    new_data : pd.DataFrame
        Y matrix, with columns same as that of X matrix.

    """
    cols_to_create = list(benefits.columns)

    # Registration processing
    df_reg = ld.load_generic_data("bocw_reg_trans")
    Y_reg = pd.DataFrame([], columns=cols_to_create, index=df_reg.index)
    direct_match = df_reg.columns[df_reg.columns.isin(cols_to_create)]
    Y_reg[direct_match] = df_reg[direct_match].copy()

    age_map = {
        col: "age" for col in cols_to_create if re.search("^age_", col) is not None
    }

    for to_col, from_col in age_map.items():
        Y_reg[to_col] = list(process_by_name(df_reg[from_col], to_col).values)

    # Claims processing
    df_claims = ld.load_generic_data("bocw_claims_trans")
    df_claims.set_index("beneficiary_name", inplace=True)
    Y_claims = reconstruct_beneficiary_profile(benefits, df_claims)

    # Join both
    Y_reg.index = Y_reg.index.astype(str)
    final_Y = Y_reg.combine(Y_claims, hlp.ret_non_na_series)

    return final_Y


def reconstruct_beneficiary_profile(benefits, schemes_availed_data):
    """
    Use availed benefits list to fill in the attributes for beneficiaries.

    For every benefit availed, the 1s are picked and placed in Y
    matrix status quo, but 0s replaced with NA.

    The function expects multiple benefits to be separated by a comma. If a
    beneficiary has claimed multiple benefits, the criteria passed are
    aggregated and non-NA values are preserved.

    Parameters
    ----------
    benefits : pd.DataFrame
        X matrix, benefits and associated eligibility criteria.
    schemes_availed_data : pd.DataFrame
        Benefits availed by beneficiaries.

    Returns
    -------
    beneficiary_Y : pd.DataFrame
        Y matrix, derived only from the claims made.

    """
    scheme_long = (
        schemes_availed_data.assign(
            scheme=schemes_availed_data["scheme"].str.split(",")
        )
        .explode("scheme")
        .scheme.str.strip()
    )
    beneficiary = (
        scheme_long.to_frame()
        .reset_index()
        .set_index(["beneficiary_name", "scheme"])
        .reindex(columns=benefits.columns)
    )
    for name, scheme_name in beneficiary.iterrows():
        try:
            beneficiary.loc[name] = benefits.loc[name[1]].replace({0: np.nan})

        except KeyError:
            pass

    beneficiary = beneficiary.reset_index().drop(["scheme"], axis=1)
    beneficiary_Y = beneficiary.groupby("beneficiary_name")[benefits.columns].agg(
        lambda l: fn.reduce(lambda a, b: hlp.return_non_na(a, b), list(l))
    )
    return beneficiary_Y


def try_backdoor_on_sample():
    """Test the backdoor function on a sample."""
    benefits = ld.load_generic_data("sample_benefits_2")
    schemes_availed_data = ld.load_generic_data("sample_beneficiary_scheme")
    ref = ld.load_generic_data("sample_impute_ref")
    Y_sample = reconstruct_beneficiary_profile(benefits, schemes_availed_data)
    Y_sample_aug = hlp.augment_eligibility(Y_sample, ref)
    return Y_sample_aug


def process_by_name(data_series, to_col):
    """
    Return a boolean for elgibility pass by interpreting the column name.

    With the way column names are defined, presence of 2 underscores would mean
    a numerical variable and 1 underscore would mean a categorical variable.

    Parameters
    ----------
    data_series : pd.Series
        Data variable to process.
    to_col : str
        Name of new column being created. Would be intepreted for operations.

    Returns
    -------
    pd.Series
        Boolean for passing of eligibility criteria.

    """
    if to_col.count("_") == 2:
        comparitive, value = to_col.split("_")[1], float(to_col.split("_")[2])
        if comparitive == "mte":
            return (data_series >= value).astype(int)
        elif comparitive == "mt":
            return (data_series > value).astype(int)
        elif comparitive == "lte":
            return (data_series <= value).astype(int)
        elif comparitive == "lte":
            return (data_series < value).astype(int)
    elif to_col.count("_") == 1:
        return (data_series == to_col.split("_")[1]).astype(int)


def create_Y_from_sample(beneficiaries_dataset, cols_to_create, impute_with=np.nan):
    """
    Load and wrangles a generic beneficiary dataset into Y matrix.

    Parameters
    ----------
    beneficiaries_dataset : str
        Name of the dataset to load. Should exist in data_sources.yml
    cols_to_create : list
        New columns to create.
    impute_with : float64
        Value to impute missing with.

    Returns
    -------
    beneficiary_x_criteria : pd.DataFrame
        Y matrix, with columns same as that of X matrix.

    """
    data = ld.load_generic_data(beneficiaries_dataset)
    variable_map = utl.load_params_file(beneficiaries_dataset)
    new_data = pd.DataFrame([], columns=cols_to_create, index=data.index)
    for to_col, from_col in variable_map.items():
        new_data[to_col] = list(process_by_name(data[from_col], to_col).values)

    beneficiary_x_criteria = impute_missing_in_Y(new_data, impute_with)
    return beneficiary_x_criteria


def impute_missing_in_Y(beneficiary_x_criteria, value):
    """
    Impute missing in Y matrix to give beneficiaries benefit of doubt.

    Parameters
    ----------
    beneficiary_x_criteria : pd.DataFrame
        Y matrix as a dataframe.
    value : float64
        Value to replace missing with.

    Returns
    -------
    imputed_data : pd.DataFrame
        Missing imputed with value in Y matrix.

    """
    imputed_data = beneficiary_x_criteria.fillna(value)
    return imputed_data
