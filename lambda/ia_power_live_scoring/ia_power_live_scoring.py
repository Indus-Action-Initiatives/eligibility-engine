import json
import boto3
from s3_util import S3_Handler

import pandas as pd

import calculation_layer as cal

s3 = boto3.client("s3")
s3r = boto3.resource("s3")
bucket = "ia-dev-sandbox-1"
util = S3_Handler(s3, s3r, bucket)


def load_benefits(handler, benefit_prefix, benefit_index):
    """Load benefits from S3 and set index column

    Parameters
    ----------
    handler : S3_Handler
        Handler object for S3 operations
    benefit_prefix : str
        S3 prefix for benefit data
    benefit_index : str
        Index column for benefit data

    Returns
    -------
    pd.DataFrame
    """
    benefits = util.load_dataframe(benefit_prefix).set_index(benefit_index)
    return benefits


def generate_message(eligibility):
    """
    Return string of eligible benefits

    Parameters
    ----------
    eligibility : pd.DataFrame
        Eligibility dataframe for benefits

    Returns
    -------
    str
        message content
    """
    benefits = eligibility[eligibility["Proximity_score"] == 1]["benefit_name"].tolist()
    return "You are eligible for " + ", ".join(benefits)


def publish_to_sms(message, phone_number):
    """
    Send text to beneficiary

    Parameters
    ----------
    message : str
        Message to send
    phone_number : str
        Phone number

    """
    sns = boto3.client("sns")
    sns.publish(PhoneNumber=phone_number, Message=message)
    return 0


def publish_to_email(destination_email, message):
    """
    Send email to verified email address

    Parameters
    ----------
    destination_email : str
    message : str

    """
    ses_client = boto3.client("ses")
    CHARSET = "UTF-8"

    response = ses_client.send_email(
        Destination={
            "ToAddresses": [
                destination_email,
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": CHARSET,
                    "Data": message,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": "IA POWER",
            },
        },
        # sorry sid
        Source="sid.ravinutala@idinsight.org",
    )
    return 0


def lambda_handler(event, context):
    print(event)

    body = json.loads(event["body"])

    beneficiary_name = body["beneficiary_name"]
    if body["sys_identifier"]:
        scored = util.load_dataframe("bocw_scored/")
        eligibility_result = scored[
            scored["beneficiary_name"].astype("str") == beneficiary_name
        ]
        print(eligibility_result)

    else:
        input_beneficiary = body["contents"]
        input_beneficiary["beneficiary_name"] = beneficiary_name
        input_beneficiary = pd.DataFrame([input_beneficiary]).set_index(
            "beneficiary_name"
        )

        print(input_beneficiary)

        benefits = load_benefits(util, "key_benefits", "benefit_name")
        print(benefits)

        score = cal.get_proximity_score(benefits, input_beneficiary)
        comments = cal.get_comments(
            benefits,
            input_beneficiary,
            beneficiary_key="beneficiary_name",
            benefit_key="benefit_name",
        )

        eligibility_result = score.rename(columns={"score": "Proximity_score"}).merge(
            comments, on=["beneficiary_name", "benefit_name"]
        )
        print(eligibility_result)

    message = generate_message(eligibility_result)
    publish_to_sms(message, body["phone_number"])

    return {"statusCode": 200, "body": json.dumps(message)}
