import src.nodes.calculation as cal
import src.nodes.checkers as chk

import pandas as pd


def test_perm_rows():
    """
    Test equivalence when rows in beneficiary are permuted
    """
    beneficiary_a = pd.DataFrame(
        [
            {"beneficiary_name": "foo", "a": 1, "b": 0},
            {"beneficiary_name": "bar", "a": 0, "b": 1},
        ]
    ).set_index("beneficiary_name")
    beneficiary_b = pd.DataFrame(
        [
            {"beneficiary_name": "bar", "a": 0, "b": 1},
            {"beneficiary_name": "foo", "a": 1, "b": 0},
        ]
    ).set_index("beneficiary_name")

    benefit = pd.DataFrame([{"benefit_name": "p1", "a": 1, "b": 0}]).set_index(
        "benefit_name"
    )

    res_a = cal.get_proximity_score(benefit, beneficiary_a)
    res_b = cal.get_proximity_score(benefit, beneficiary_b)

    assert res_a.reset_index(drop=True).equals(
        res_b.reset_index(drop=True)
    ), "Row permutations should not affect output"


def test_perm_cols():
    """
    Test behaviour when columns in benefits matrix are permuted
    """
    beneficiary = pd.DataFrame(
        [
            {"beneficiary_name": "foo", "a": 1, "b": 0},
            {"beneficiary_name": "bar", "a": 0, "b": 1},
        ]
    ).set_index("beneficiary_name")

    benefit_a = pd.DataFrame([{"benefit_name": "p1", "b": 0, "a": 1}]).set_index(
        "benefit_name"
    )
    benefit_b = pd.DataFrame([{"benefit_name": "p1", "a": 1, "b": 0}]).set_index(
        "benefit_name"
    )

    try:
        chk.check_matrix_sanity(benefit_a, beneficiary)
        chk.check_matrix_sanity(benefit_b, beneficiary)

        res_a = cal.get_proximity_score(benefit_a, beneficiary)
        res_b = cal.get_proximity_score(benefit_b, beneficiary)

        assert res_a.reset_index(drop=True).equals(
            res_b.reset_index(drop=True)
        ), "Column permutations should not affect output"

    except ValueError:
        pass


def test_value_correctness():
    """
    Test if proximity scores are correctly assigned
    """
    beneficiary = pd.DataFrame(
        [
            {"beneficiary_name": "foo", "a": 1, "b": 0},
            {"beneficiary_name": "bar", "a": 0, "b": 1},
            {"beneficiary_name": "moo", "a": None, "b": 1},
        ]
    ).set_index("beneficiary_name")

    benefit = pd.DataFrame([{"benefit_name": "p1", "a": 1, "b": 0}]).set_index(
        "benefit_name"
    )

    chk.check_matrix_sanity(benefit, beneficiary)

    res_a = cal.get_proximity_score(benefit, beneficiary)

    assert (
        (res_a.loc[res_a["beneficiary_name"] == "foo", "score"].iloc[0] == 1)
        & (res_a.loc[res_a["beneficiary_name"] == "bar", "score"].iloc[0] == -1)
        & (res_a.loc[res_a["beneficiary_name"] == "moo", "score"].iloc[0] == 0)
    ), "Values are not assigned according to design"
