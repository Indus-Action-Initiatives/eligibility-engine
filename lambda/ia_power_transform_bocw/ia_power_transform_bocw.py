from s3_util import S3_Handler
import numpy as np

import transforms
import boto3

import json

s3 = boto3.client("s3")
s3r = boto3.resource("s3")
bucket = "ia-dev-sandbox-1"
util = S3_Handler(s3, s3r, bucket)

bocw_benefit_map = {
    "Maternity.*": "BoCW Maternity benefits",
    ".*Edu.*": "BoCW Financial assistance for education",
    ".*Marriage": "BoCW Financial assistance for marriage of children",
    "Pension.*": "BoCW Pension benefit",
    "^Death$": "BoCW Death benefit",
    "Death & Funeral": "BoCW Death benefit",
}

MODE = "dev"

def get_bocw_beneficiary(bocw_prefix, config_prefix, params=None):

    """
    Extract BoCW raw data set
    Transform into beneficiary columns
    Write /return output indexed by registration number

    Parameters
    ----------
    bocw_prefix : str
        location of bocw dataset
    config_prefix : str
        location of config file
    params : dict, optional
        by default None

    Returns
    -------
    pd.DataFrame
        output dataframe with transformed bocw columns
    """

    if not params:
        params = util.load_yaml(config_prefix)
    columns = params["bocw_useful_columns"] + ["Registration No"]
    mapping = params["bocw_target_columns"]
    bocw = util.load_dataframe(bocw_prefix)

    transformed_df = transforms.bocw_transform(bocw[columns], columns, mapping)
    return transformed_df


def get_bocw_claims(bocw_claims_prefix):
    """
    Load and process BoCW claims data.
    Column names and indices are set, and multiple schemes collapsed.

    Parameters
    ----------
    bocw_claims_prefix : str
        location of bocw claims dataset

    Returns
    -------
    df_claims_combined : pd.DataFrame
        Claims made by beneficiaries, identified by registration number.

    """
    bocw_claims_data = util.load_generic_data(bocw_claims_prefix)
    bocw_claims_data.columns = bocw_claims_data.iloc[0]

    df_claims = bocw_claims_data[["Reg. No.", "Benefit"]].loc[
        1:,
    ]
    df_claims["scheme"] = df_claims.Benefit.replace(bocw_benefit_map, regex=True)
    df_claims.drop_duplicates(subset=["Reg. No.", "scheme"], inplace=True)
    df_claims = df_claims.rename(columns={"Reg. No.": "beneficiary_name"})
    df_claims_combined = (
        df_claims.groupby(["beneficiary_name"])["scheme"]
        .apply(lambda x: ",".join(x))
        .reset_index()
    )
    return df_claims_combined


def lambda_handler(event, context):
    # TODO implement
    trans_bocw = get_bocw_beneficiary("bocw_data", "config/parameters.yml")
    
    if MODE == "dev":
        cols_nullable = [_ for _ in trans_bocw.columns if _ != "beneficiary_name"]
        trans_bocw[cols_nullable] = trans_bocw[cols_nullable].mask(np.random.random(trans_bocw[cols_nullable].shape) < 0.3)

    util.write_dataframe_with_header(
        "bocw_transformed/bocw_reg_beneficiary.csv", trans_bocw, index_flag=False
    )

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
