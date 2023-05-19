import boto3
from s3_util import S3_Handler

import calculation_layer as cal

s3 = boto3.client("s3")
s3r = boto3.resource("s3")
bucket = "ia-dev-sandbox-1"
util = S3_Handler(s3, s3r, bucket)


def load_benefits(handler, benefit_prefix, benefit_name, benefit_index):
    """Load specific benefit from S3

    Parameters
    ----------
    handler : S3_Handler
        Handler for S3 operations
    benefit_prefix : str
        s3 prefix for benefit data
    benefit_name : str
        name of benefit
    benefit_index : str
        name of index col

    Returns
    -------
    pd.DataFrame
    """
    benefits = util.load_dataframe(benefit_prefix).set_index(benefit_index)
    benefits = benefits[benefits.index == benefit_name].copy()
    return benefits


def generate_message(eligibility):
    benefits = eligibility[eligibility["Proximity_score"] == 1]["benefit_name"].tolist()
    return "You are eligible for " + ", ".join(benefits)


def lambda_handler(event, context):
    print(event)
    benefit_name = event["body"][0]

    # beneficiary_dataset = "bocw_Y_transformed"
    # benefit_dataset = "key_benefits.csv"

    # benefit_dataset = event["benefit_prefix"]
    # beneficiary_dataset = event["beneficiary_prefix"]
    benefit_dataset = event["body"][1]
    beneficiary_dataset = event["body"][2]

    input_beneficiary = util.load_dataframe(beneficiary_dataset).set_index(
        "beneficiary_name"
    )
    input_beneficiary = input_beneficiary.astype(float)
    print(input_beneficiary.dtypes)

    benefits = load_benefits(util, benefit_dataset, benefit_name, "benefit_name")
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

    probabilities = util.load_dataframe("bocw_prob_summary/prob_score_summary.csv")
    if probabilities is None:
        eligibility_result["Probability_score"] = "Not calculated"
    else:
        eligibility_result = eligibility_result.merge(
            probabilities, on=["beneficiary_name", "benefit_name"], how="left"
        )

    util.write_dataframe_with_header(
        "bocw_scored/{}.csv".format(benefit_name), eligibility_result, index_flag=False
    )

    return {"statusCode": 200, "body": "Scoring completed!"}
