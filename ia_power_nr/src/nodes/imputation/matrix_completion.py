from abc import ABC, abstractmethod
from sklearn.preprocessing import StandardScaler


class MatrixCompletion(ABC):
    """
    Abstract class for all matrix completion methods
    """

    def __init__(self, scale_mean, scale_std):
        self.fitted = False
        self.scaler = StandardScaler(with_mean=scale_mean, with_std=scale_std)

    @abstractmethod
    def fit(self, beneficiary_matrix):
        self.beneficiary_matrix = beneficiary_matrix
        self.beneficiaries = beneficiary_matrix.index.to_list()
        self.demographics = beneficiary_matrix.columns.to_list()
        self.fitted = True

    @abstractmethod
    def sample(self, N_samples):
        if not self.fitted:
            raise ValueError("Please run .fit() before sample()")
