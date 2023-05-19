import json
import boto3
from s3_util import S3_Handler

import pandas as pd

import calculation_layer as cal

s3 = boto3.client("s3")
s3r = boto3.resource("s3")
bucket = "ia-dev-sandbox"
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


def lambda_handler(event, context):
    print(event)

    body = json.loads(event["body"])

    full_results = []

    programs = body["programs"]

    benefit_df = pd.DataFrame(
        [
            {
                "programUuid": program["programUuid"],
                "programName": program["programName"],
                **program["eligibilityCriteria"],
            }
            for program in programs
        ]
    )

    benefit_df["benefit_name"] = (
        benefit_df["programUuid"] + "__" + benefit_df["programName"]
    )

    benefits = (
        benefit_df[
            [_ for _ in benefit_df.columns if _ not in ["programUuid", "programName"]]
        ]
        .set_index("benefit_name")
        .fillna(0)
    )

    for input_beneficiary in body["beneficiaries"]:

        beneficiary_name = input_beneficiary["beneficiaryUuid"]
        input_beneficiary = (
            pd.DataFrame([input_beneficiary])
            .rename(columns={"beneficiaryUuid": "beneficiary_name"})
            .set_index("beneficiary_name")
        )

        input_beneficiary[
            [_ for _ in benefits.columns if _ not in input_beneficiary.columns]
        ] = None

        score = cal.get_proximity_score(benefits, input_beneficiary)
        comments = cal.get_comments(
            benefits,
            input_beneficiary,
            beneficiary_key="beneficiary_name",
            benefit_key="benefit_name",
        )

        eligibility_result = (
            score.merge(
                benefit_df[["benefit_name", "programName", "programUuid"]],
                how="left",
                on=["benefit_name"],
            )
            .merge(comments, on=["beneficiary_name", "benefit_name"])
            .rename(
                columns={
                    "score": "proximityScore",
                    "Criteria Failed": "criteriaFailed",
                    "Criteria Passed": "criteriaPassed",
                    "Missing Info": "missingData",
                }
            )[
                [
                    "programName",
                    "programUuid",
                    "proximityScore",
                    "criteriaFailed",
                    "criteriaPassed",
                    "missingData",
                ]
            ]
        )

        message = eligibility_result.to_json(orient="records")
        full_results.append(
            {"beneficiaryUuid": beneficiary_name, "benefitEligibility": message}
        )

    return {"statusCode": 200, "body": json.dumps(full_results)}
