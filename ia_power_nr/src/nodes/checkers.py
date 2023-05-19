""" Checkers of matrices."""
import logging


def check_matrix_sanity(benefit, beneficiary):
    """
    Check if the matrices are sane for multiplication.

    1) Column count and names should match exactly.
    2) Benefits matrix shouldn't have NAs.
    3) Beneficiary matrix shouldn't have NAs. Should be imputed.

    Parameters
    ----------
    benefit : pd.DataFrame
        X matrix.
    beneficiary : pd.DataFrame
        Y matrix.

    Returns
    -------
    Returns if all sanity checks passed.

    """
    if sum(benefit.columns == beneficiary.columns) != len(benefit.columns):
        columns_only_in_benefit = set(benefit.columns) - set(beneficiary.columns)
        columns_only_in_beneficary = set(beneficiary.columns) - set(benefit.columns)
        raise ValueError(
            (
                "Columns of benefit and beneficiary datasets are different\n"
                f"   Columns in Benefit but not in Beneficiary: {columns_only_in_benefit}\n"  # noqa: E501
                f"   Columns in Beneficiary but not in Benefits: {columns_only_in_beneficary}"  # noqa: E501
            )
        )
    elif benefit.isna().any(axis=None):
        raise ValueError("Cannot have NAs in Benefits dataset")
    elif any(benefit.sum(axis=1) == 0):
        no_eli = list(benefit.index[benefit.sum(axis=1) == 0])
        raise ValueError(f"No eligibility criteria for benefits: {no_eli}")
    logging.info(
        (f"Columns match and no NAs; {len(benefit.columns)}" " columns in matrices")
    )
    return True


def check_matrix_shape(X, Y, Q=None):
    """
    Check if shape of X, Y and Q matrices are sane.

    Parameters
    ----------
    X : np.array
        X matrix.
    Y : np.array
        Y matrix.
    Q : np.array, optional
        Weight matrix. The default is None.

    Raises
    ------
    ValueError
        If shapes do not match.

    Returns
    -------
    None.

    """
    if Q is None:
        if X.shape[1] != Y.shape[1]:
            raise ValueError("Shape of X and Y matrices not in agreement")
    elif (
        (X.shape[1] != Y.shape[1])
        or (X.shape[1] != Q.shape[1])
        or (Q.shape[1] != Q.shape[0])
    ):
        raise ValueError("Shape of X, Y, and Q matrices not in agreement")
    return
