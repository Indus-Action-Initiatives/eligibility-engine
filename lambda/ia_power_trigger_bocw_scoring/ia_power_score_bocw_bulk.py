import json
import boto3

from s3_util import S3_Handler

s3 = boto3.client("s3")
s3r = boto3.resource("s3")
bucket = "ia-dev-sandbox-1"
util = S3_Handler(s3, s3r, bucket)


def lambda_handler(event, context):

    benefit_prefix = event["benefit_prefix"]
    beneficiary_prefix = event["beneficiary_prefix"]
    account_name = event["account_name"]

    benefits = util.load_dataframe(benefit_prefix)

    benefits = benefits["benefit_name"].unique()

    benefit_dict = [
        {
            "benefit_name": benefit,
            "benefit_prefix": benefit_prefix,
            "beneficiary_prefix": beneficiary_prefix,
        }
        for benefit in benefits
    ]

    client = boto3.client("stepfunctions")
    response = client.start_execution(
        stateMachineArn="arn:aws:states:ap-south-1:{}:stateMachine:ia_power_score_bocw_bulk".format(
            account_name
        ),
        input=json.dumps(
            {
                "benefits": benefit_dict,
            }
        ),
    )

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
