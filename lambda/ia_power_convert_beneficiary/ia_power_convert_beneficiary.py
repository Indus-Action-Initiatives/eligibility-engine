import json

from s3_util import S3_Handler
import boto3

import ia_beneficiary as clm
import helper as hlp

s3 = boto3.client("s3")
s3r = boto3.resource("s3")
bucket = "ia-dev-sandbox-1"
util = S3_Handler(s3, s3r, bucket)

CONSIDER_PAST_CLAIMS = False


def lambda_handler(event, context):

    benefits = util.load_dataframe("key_benefits").set_index("benefit_name")

    beneficiary_Y = clm.get_Y_from_bocw(
        util, benefits, "bocw_transformed", "bocw_claims_trans"
    )

    clm.check_matrix_sanity(benefits, beneficiary_Y)

    if CONSIDER_PAST_CLAIMS:
        impute_ref = util.load_dataframe("impute_ref")
        beneficiary_Y = hlp.augment_eligibility(beneficiary_Y, impute_ref)

    util.write_dataframe_with_header(
        "bocw_Y_transformed/beneficiary_Y.csv", beneficiary_Y
    )

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
