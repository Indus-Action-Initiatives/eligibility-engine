"""Probability calculation and scoring module."""
import numpy as np
import pandas as pd
from warnings import warn

import load_dependency

import bootstrap_matrix_completion as boot
import calculation_layer as cal
import helper as hlp
import ia_beneficiary as clm

from s3_util import S3_Handler
import boto3

# initiate s3 handler
s3 = boto3.client("s3")
s3r = boto3.resource("s3")
bucket = "ia-dev-sandbox-1"
util = S3_Handler(s3, s3r, bucket)

MODE = "prod"


def lambda_handler(event, context):

    benefit_location = event["body"][0]
    indexer = event["body"][1]
    benefit_name = event["body"][2]

    get_bocw_probability(benefit_location, benefit_name, indexer)

    return {"statusCode": 200, "body": "Scoring completed!"}


def get_bocw_probability(benefit_location, benefit_name, indexer):
    """
    Use bootstrapped-imputed samples of BoCW registration and claims data
    to calculate the probability of eligibility.

    Since registration data does not have missing information, 10% random data
    points are explicitly masked. Variables that are entirely absent are
    imputed with 1 if ignore_full_missing is set True.

    Parameters
    ----------
    benefit_location : str
        Prefix for benefits and associated criteria.
    benefit_name : str
        Name of benefit to score.
    indexer : int
        Current sampling frame

    Returns
    -------
    probs : pd.Series
        Probability scores for eligibility of benefits.

    """
    benefits = util.load_dataframe(benefit_location)
    benefits = benefits[benefits["benefit_name"] == benefit_name].copy()
    print(benefits.columns)
    df_reg = util.load_dataframe(
        "bocw_transformed/bocw_reg_beneficiary.csv", table=[]
    ).set_index("beneficiary_name")
    print(df_reg.columns)
    print(df_reg.isnull().any())

    if MODE == "dev":
        # df_reg = df_reg.sample(500)  # remove in production
        df_reg = df_reg.mask(np.random.random(df_reg.shape) < 0.3)

    # check if there are nulls
    if not df_reg.isnull().any().any():
        return None

    numeric_cols = ["age"]
    categorical_cols = [col for col in df_reg.columns if col != "age"]

    df_reg[categorical_cols] = df_reg[categorical_cols].astype(float)

    df_sampled = run_matrix_completion(
        df_reg,
        numeric_cols,
        categorical_cols,
    )
    probs = calculate_probability(benefits, df_sampled)

    if probs is not None:
        util.write_dataframe_with_header(
            "bocw_prob_score_samples/bocw_full_prob_score_{}_{}.csv".format(
                indexer, benefit_name
            ),
            probs,
        )

    return 0


def run_matrix_completion(
    df_with_missing,
    numeric_cols,
    categorical_cols,
):
    """
    Run Matrix Completion algorithm to impute missing data and return imputed samples.

    If the original dataframe (with no missing values) is provided, imputation
    performance is calculated.

    Parameters
    ----------
    df_with_missing : pd.DataFrame
        Dataframe with missing values.
    numeric_cols : list(str)
        List of numeric columns.
    categorical_cols : list(str)
        List of categorical columns.
    df_original : pd.DataFrame, optional
        Original dataframe with no missing values.

    Returns
    -------
    df_sampled : list(pd.DataFrame)
        Sampled list of dataframes where missing values were imputed.

    """
    bmc = boot.BootstrapMatrixCompletion("iterative", "knn", True, True, False)
    print(df_with_missing.columns, df_with_missing.shape, numeric_cols,categorical_cols)
    bmc.fit(df_with_missing, numeric_cols, categorical_cols)
    df_sampled = bmc.sample(3)

    return df_sampled


def calculate_probability(benefits, df_sampled):
    """
    Calcuate probability by averaging the eligibility across all imputed samples.

    Parameters
    ----------
    benefits : pd.DataFrame
        X matrix - list of benefits and associated criteria.
    df_sampled : list(pd.DataFrame)
        Sampled list of dataframes where missing values were imputed.

    Returns
    -------
    probs : pd.Series
        Probability scores for eligibility of benefits.

    """
    all_scores = pd.DataFrame()
    for df in df_sampled:
        print(df.loc[58, "married_yes"])
        all_scores = all_scores.append(score_sample_bocw(benefits.set_index("benefit_name"), df))
    print(all_scores.shape)
    if all_scores is None:
        probs = None
    elif all_scores.empty:
        probs = None
    else:
        all_scores_long = cal.reshape_to_long(all_scores)
        probs = (
            all_scores_long.groupby(["beneficiary_name", "benefit_name"])
            .score.mean()
            .rename("Probability_score")
        )

    return probs


def score_sample_bocw(benefits, df_sample):
    """
    Score a sampled BoCW beneficiary dataset, with score being 'eligible' or 'ineligible'

    Parameters
    ----------
    benefits : pd.DataFrame
        X matrix - list of benefits and associated criteria.
    df_sample: pd.DataFrame
        A sampled dataframe from the completion method.

    Returns
    -------
    output : pd.DataFrame
        Eligibility (bool) for each combination of benefit and beneficiary.

    """
    # impute_ref = util.load_dataframe("impute_ref", table=[])
    X = np.array(benefits)

    df = df_sample.astype(float)
    final_Y = clm.get_Y_from_bocw(util, benefits, df, "bocw_claims_trans")
    # final_Y = hlp.augment_eligibility(final_Y, impute_ref)

    if all(final_Y.isna().sum() == len(final_Y)) & (MODE == "prod"):
        output = None

        # TODO handle this error
        warn(
            "Some columns are entirely missing. Eligibility cannot be calculated. "
            "Thus skipping probability calculation."
        )
    else:
        output = cal._take_bitwise_product(X, np.array(final_Y.fillna(0), dtype="int"))
        output = pd.DataFrame(
            output,
            index=final_Y.index,
            columns=benefits.index,
        )
    return output
