import pandas as pd

import boto3
from s3_util import S3_Handler

# initiate s3 handler
s3 = boto3.client("s3")
s3r = boto3.resource("s3")
bucket = "ia-dev-sandbox-1"
util = S3_Handler(s3, s3r, bucket)


def lambda_handler(event, context):

    full_prob_scores = util.load_dataframe("bocw_prob_score_samples/")

    prob_scores_summary = full_prob_scores.groupby(
        ["beneficiary_name", "benefit_name"]
    )["Probability_score"].mean()

    util.write_dataframe_with_header(
        "bocw_prob_summary/prob_score_summary.csv",
        prob_scores_summary,
    )

    return {"statusCode": 200, "body": "Scoring completed!"}