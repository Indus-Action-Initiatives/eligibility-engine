import src.nodes.beneficiary as clm
import src.nodes.calculation as cal
import src.nodes.checkers as chk
import pandas as pd


def test_bad_values():
    """Check if nonsense value in beneficiary table breaks pipeline

    Returns
    -------
    0
        If the pipeline errors out correctly
        Else the test fails
    """
    beneficiary = pd.DataFrame(
        [
            {"beneficiary_name": "foo", "a": 1, "b": 0},
            {"beneficiary_name": "bar", "a": 0, "b": 1},
        ]
    ).set_index("beneficiary_name")

    benefit = pd.DataFrame([{"benefit_name": "p1", "a": 1, "b": 0}]).set_index(
        "benefit_name"
    )

    beneficiary.loc["foo", "a"] = "blah123"
    chk.check_matrix_sanity(benefit, beneficiary)
    try:
        cal.get_proximity_score(benefit, beneficiary)
    except ValueError:
        return 0

    assert False, "Pipeline should fail for string valued columns"


def test_empty_beneficiary():
    """
    check if pipeline fails when beneficiary table has no rows

    Returns
    -------
    0
        Test succeeds if pipeline fails
        Otherwise, if proximity score turns, test fails
    """
    beneficiary = pd.DataFrame(columns=["beneficiary_name", "a", "b"]).set_index(
        "beneficiary_name"
    )

    benefit = pd.DataFrame([{"benefit_name": "p1", "a": 1, "b": 0}]).set_index(
        "benefit_name"
    )

    chk.check_matrix_sanity(benefit, beneficiary)
    try:
        cal.get_proximity_score(benefit, beneficiary)
    except ValueError:
        return 0

    assert False, "Pipeline should fail when input beneficiary data is empty"


def test_empty_benefits():
    """Test behaviour when benefit table is empty

    Returns
    -------
    0
        Test succeeds if the pipeline fails with no benefits
        Otherwise, test fails if proximity score returns
    """

    beneficiary = pd.DataFrame(
        [
            {"beneficiary_name": "foo", "a": 1, "b": 0},
            {"beneficiary_name": "bar", "a": 0, "b": 1},
        ]
    ).set_index("beneficiary_name")

    benefit = pd.DataFrame(columns=["benefit_name", "a", "b"]).set_index("benefit_name")

    chk.check_matrix_sanity(benefit, beneficiary)
    try:
        cal.get_proximity_score(benefit, beneficiary)
    except ValueError:
        return 0

    assert False, "Pipeline should fail when input benefits  data is empty"


def test_benefits_columns():
    """
    Test if pipeline works when:
    there are more columns in beneficiary matrix than benefits
    """

    beneficiary = pd.DataFrame(
        [
            {"beneficiary_name": "foo", "a": 1, "b": 0},
            {"beneficiary_name": "bar", "a": 0, "b": 1},
        ]
    ).set_index("beneficiary_name")

    benefit = pd.DataFrame([{"benefit_name": "p1", "a": 1}]).set_index("benefit_name")
    try:
        chk.check_matrix_sanity(benefit, beneficiary)
        cal.get_proximity_score(benefit, beneficiary)
    except ValueError:
        assert (
            False
        ), "Pipeline should not fail when benefits has fewer columns than beneficiaries"


def test_beneficiary_columns():
    """Test if beneficiary table has fewer columns than benefits

    Returns
    -------
    0
        Test succeeds if the pipeline errors out
    """

    beneficiary = pd.DataFrame(
        [
            {"beneficiary_name": "foo", "a": 1},
            {"beneficiary_name": "bar", "a": 0},
        ]
    ).set_index("beneficiary_name")

    benefit = pd.DataFrame([{"benefit_name": "p1", "a": 1, "b": 0}]).set_index(
        "benefit_name"
    )
    try:
        chk.check_matrix_sanity(benefit, beneficiary)
        cal.get_proximity_score(benefit, beneficiary)
    except (ValueError, IndexError):
        return 0

    assert (
        False
    ), "Pipeline should fail when beneficiaries have fewer columns than benefits"


def test_backdoor():
    """
    If a benefit availed by a beneficiary is not in a benefit list,
    it should be ignored for feature reconstruction.
    """
    benefit = pd.DataFrame(
        {"benefit_name": ["p1", "p2"], "a": [1, 0], "b": [0, 1]}
    ).set_index("benefit_name")

    schemes_availed = pd.DataFrame(
        [
            {"beneficiary_name": "foo", "scheme": "p1"},
            {"beneficiary_name": "bar", "scheme": "p3"},
        ]
    ).set_index("beneficiary_name")

    recons = clm.reconstruct_beneficiary_profile(benefit, schemes_availed)
    assert (
        recons.loc["bar"].isna().sum() == 2
    ), "Attempt to reconstruct using a benefit not in benefit list"
