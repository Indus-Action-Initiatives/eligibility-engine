"""Matrix Completion Abstract Class."""
from abc import ABC, abstractmethod
from sklearn.preprocessing import StandardScaler
from warnings import warn


class MatrixCompletion(ABC):
    """Abstract class for all matrix completion methods."""

    def __init__(self, scale_mean, scale_std, raise_if_all_missing):
        self.fitted = False
        self.scaler = StandardScaler(with_mean=scale_mean, with_std=scale_std)
        self.raise_if_all_missing = raise_if_all_missing

    @abstractmethod
    def fit(self, beneficiary_matrix):
        self.beneficiary_matrix = beneficiary_matrix
        self.beneficiaries = self.beneficiary_matrix.index.to_list()
        self.demographics = self.beneficiary_matrix.columns.to_list()
        self.fitted = True
        self.full_missing_variables = beneficiary_matrix.isna().sum() == len(
            beneficiary_matrix
        )
        # if any(self.full_missing_variables):
        #     full_missing_column_names = list(
        #         self.full_missing_variables[self.full_missing_variables].columns
        #     )
        #     if self.raise_if_all_missing:
        #         raise ValueError(
        #             (
        #                 "The following columns have no information: "
        #                 f"{full_missing_column_names}. "
        #                 "Aborting."
        #             )
        #         )
        #     else:
        #         warn(
        #             (
        #                 "The following columns have no information: "
        #                 f"{full_missing_column_names}. "
        #                 "These will not be imputed"
        #             )
        #         )

    @abstractmethod
    def sample(self, N_samples):
        if not self.fitted:
            raise ValueError("Please run .fit() before sample()")
