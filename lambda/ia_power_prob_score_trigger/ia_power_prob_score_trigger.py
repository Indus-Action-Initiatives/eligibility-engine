import json
import boto3
from itertools import product

from s3_util import S3_Handler

s3 = boto3.client("s3")
s3r = boto3.resource("s3")
bucket = "ia-dev-sandbox-1"
util = S3_Handler(s3, s3r, bucket)


def clean_directory(util, output_location, token=""):

    if token == "":
        response = util.s3.list_objects_v2(Bucket=util.bucket, Prefix=output_location)
    else:
        response = util.s3.list_objects_v2(
            Bucket=util.bucket, Prefix=output_location, ContinuationToken=token
        )

    truncboolean = response["IsTruncated"]

    if "Contents" in response.keys():
        for key in response["Contents"]:
            files = key["Key"]
            util.s3r.Object(util.bucket, files).delete()

    if truncboolean:
        token = response["NextContinuationToken"]
        util.clean_directory(output_location, token)


def lambda_handler(event, context):

    benefit_prefix = event["benefit_prefix"]
    n_samples = event["n_samples"]
    account_name = event["account_name"]

    clean_directory(util, "bocw_prob_score_samples/")

    iterator = list(range(n_samples))

    benefits = util.load_dataframe(benefit_prefix)

    benefits = benefits["benefit_name"].unique()

    sample_dict = [
        {"benefit_prefix": benefit_prefix, "indexer": k, "benefit_name": b}
        for k, b in product(iterator, benefits)
    ]

    client = boto3.client("stepfunctions")
    response = client.start_execution(
        stateMachineArn="arn:aws:states:ap-south-1:{}:stateMachine:ia_power_bocw_etl".format(
            account_name
        ),
        input=json.dumps(
            {
                "sample_mapper": sample_dict,
            }
        ),
    )

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
