import numpy as np
import pandas as pd
import src.nodes.checkers as chk
from src.utils import save_output
from itertools import product


@save_output("recommendation_comments")
def get_comments(benefits_data, beneficiary_data):
    """
    Generate comments on missing, failed and passed criteria.

    Parameters
    ----------
    benefits_data : pd.DataFrame
        Benefits data (X matrix)
    beneficiary_data : pd.DataFrame
        Fully processed beneficiary data (Y matrix).

    Returns
    -------
    result_long : pd.DataFrame
        Beneficiary X Benefits comments in long format.

    """
    X = np.array(benefits_data)
    Y0 = np.array(beneficiary_data.fillna(0), dtype="int64")

    inner_product = np.array(
        np.array(_take_inner_product(X, Y0, np.diag(np.ones(len(X.T)))), dtype="int64"),
        dtype="str",
    )
    max_score = np.array(
        np.array(_get_max_score(X, np.diag(np.ones(len(X.T)))), dtype="int64"),
        dtype="str",
    )

    passing = pd.DataFrame(
        np.char.add(inner_product, np.char.add(" of ", max_score)),
        index=beneficiary_data.index,
        columns=benefits_data.index,
    )

    passing_long = reshape_to_long(passing)

    collection = pd.DataFrame()
    for benefit in benefits_data.index:
        reqd_beneficiary_data = beneficiary_data.loc[
            :, benefits_data.loc[benefit].isin([1])
        ]
        df_with_comments = (
            reqd_beneficiary_data.apply(lambda x: generate_comments(x), axis=1)
            .reset_index()
            .rename({0: "Comments"}, axis=1)
        )

        df_with_comments[
            ["Criteria Failed", "Criteria Passed", "Missing Info"]
        ] = df_with_comments["Comments"].tolist()
        df_with_comments.drop("Comments", axis=1, inplace=True)

        df_with_comments.insert(loc=1, column="benefit_name", value=benefit)
        collection = pd.concat([collection, df_with_comments], axis=0)

    result_long = collection.merge(
        passing_long.rename(columns={"score": "# Criteria Passed"}),
        on=["beneficiary_name", "benefit_name"],
    )
    return result_long


def generate_comments(row):
    """ Return failed, passed and missing criteria"""
    str1 = ", ".join(row[row == 0].index)
    str2 = ", ".join(row[row == 1].index)
    str3 = ", ".join(row[row.isnull()].index)
    return str1, str2, str3


@save_output("recommendation_proximity")
def get_proximity_score(benefits_data, beneficiary_data, Q=None):
    """
    Create Beneficiary X Benefits scores by matrix and bitwise multiplication.

    The score represents proportion of criteria passed only for the cases where
    some needed information is missing but other criteria are passed.

    If any of the available information results in failing of a criteria, 0
    is assigned for a score.

    Parameters
    ----------
    benefits_data : pd.DataFrame
        Benefits data (X matrix)
    beneficiary_data : pd.DataFrame
        Fully processed beneficiary data (Y matrix).
    Q : np.array, optional
        Weight matrix Q. Identity if none provided.

    Returns
    -------
    output_long : pd.DataFrame
        Beneficiary X Benefits scores in long format.

    """
    X = np.array(benefits_data)

    if Q is None:
        Q = np.diag(np.ones(len(X.T)))

    if Q.ndim == 1:
        Q = np.diag(Q)

    Y0 = np.array(beneficiary_data.fillna(0), dtype="int64")
    Y1 = np.array(beneficiary_data.fillna(1), dtype="int64")
    chk.check_matrix_shape(X, Y0)
    change = np.logical_or(_take_bitwise_product(X, Y1), _take_bitwise_product(X, Y0))

    ip = _take_inner_product(X, Y0, Q)
    score = ip / _get_max_score(X, Q)
    score[~change] = -1
    # change = False corresponds to cases that were still fails
    # even when all nulls were filled with 1 - this means some
    # other available info must be failing.

    output = pd.DataFrame(
        score,
        index=beneficiary_data.index,
        columns=benefits_data.index,
    )
    output_long = reshape_to_long(output)
    output_long["Outcome"] = "Insufficient Information"
    output_long.loc[output_long.score == 1, "Outcome"] = "Eligible"
    output_long.loc[output_long.score == -1, "Outcome"] = "Ineligible"

    return output_long


def _take_inner_product(X, Y, Q):
    """ Inner product: YQX' """
    return Y @ Q @ X.T


def _get_max_score(X, Q):
    """ Denominator for scoring: ColSum(XQ) """
    return np.sum(np.dot(X, Q), axis=1)


def _take_bitwise_product(X, Y):
    """
    Conduct bitwise operation on X and Y matrices.

    Parameters
    ----------
    X : np.array
        X matrix.
    Y : np.array
        Y matrix.

    Returns
    -------
    uv : np.array
        Output array.

    """
    uv = np.zeros(shape=(len(Y), len(X)))
    for (i, j) in product(range(len(X)), range(len(Y))):
        uv[j, i] = fold(lambda x, y: x & y, fold(star, [X[i], Y[j]]))
    return uv


def fold(operator, array):
    """ Reduce an operator over dimension."""
    return np.frompyfunc(operator, 2, 1).reduce(array, dtype=object)


def star(x, y):
    """ Non-commutative implies operation."""
    return (0, 1)[(not x) or y]


def reshape_to_long(data):
    """
    Convert score matrix to long format.

    Parameters
    ----------
    data : pd.DataFrame
        Score output.

    Returns
    -------
    data_long : pd.DataFrame
        Long formatted scores for Beneficiary X Benefits.

    """
    data_long = data.unstack().to_frame().reset_index().rename(columns={0: "score"})
    data_long = data_long[["beneficiary_name", "benefit_name", "score"]].sort_values(
        ["beneficiary_name", "score"], ascending=[True, False]
    )

    return data_long
