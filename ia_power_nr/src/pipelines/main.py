"""
Main pipeline script to recommend benefits.

Stand-alone run: `python -m src.pipelines.main`
from base `ia_power` folder
"""

import src.nodes.load_data as ld
import src.nodes.benefits as bft
import src.nodes.beneficiary as clm
import src.nodes.calculation as cal
import src.nodes.checkers as chk
import src.nodes.helper as hlp
import logging

from src.utils import save_output
from pathlib import Path


@save_output("recommendation_full")
def recommend_bocw():
    """Score BoCW CW Registration and Claims Data"""
    benefits = bft.load_benefits_matrix("key_benefits")
    beneficiary_Y = clm.get_Y_from_bocw(benefits)
    chk.check_matrix_sanity(benefits, beneficiary_Y)

    impute_ref = ld.load_generic_data("key_impute_ref")
    beneficiary_Y = hlp.augment_eligibility(beneficiary_Y, impute_ref)

    score = cal.get_proximity_score(benefits, beneficiary_Y)
    comments = cal.get_comments(benefits, beneficiary_Y)
    result = score.rename(columns={"score": "Proximity_score"}).merge(
        comments, on=["beneficiary_name", "benefit_name"]
    )

    return result


def recommend_sample_2():
    """ Sample recommender pipeline for sample dataset 2. """
    benefits_x_criteria = bft.load_benefits_matrix("sample_benefits_2")
    beneficiary_x_criteria = ld.load_generic_data("sample_beneficiary_2")

    chk.check_matrix_sanity(benefits_x_criteria, beneficiary_x_criteria)
    score = cal.get_proximity_score(benefits_x_criteria, beneficiary_x_criteria)
    comments = cal.get_comments(benefits_x_criteria, beneficiary_x_criteria)

    result = score.rename(columns={"score": "Proximity_score"}).merge(
        comments, on=["beneficiary_name", "benefit_name"]
    )

    return result


def recommend_sample_1():
    """ Sample recommender pipeline for sample dataset 1. """
    benefits_x_criteria = bft.load_benefits_matrix("sample_benefits_1")

    beneficiary_x_criteria = clm.create_Y_from_sample(
        "sample_beneficiary_pii", list(benefits_x_criteria.columns)
    )

    chk.check_matrix_sanity(benefits_x_criteria, beneficiary_x_criteria)
    score = cal.get_proximity_score(benefits_x_criteria, beneficiary_x_criteria)
    comments = cal.get_comments(benefits_x_criteria, beneficiary_x_criteria)

    result = score.rename(columns={"score": "Proximity_score"}).merge(
        comments, on=["beneficiary_name", "benefit_name"]
    )
    return result


if __name__ == "__main__":

    logging.captureWarnings(True)
    logging_path = Path(__file__).parent / "../../logs/"
    logging.basicConfig(
        filename=logging_path / "./main_pipeline.log",
        format="%(asctime)s %(levelname)s:%(message)s",
        level=logging.INFO,
    )

    logging.info("Recommending benefits")
    logging.info("-------------------------------")
    prediction = recommend_sample_2()
    logging.info("Finished recommending")
    logging.info("-------------------------------")
