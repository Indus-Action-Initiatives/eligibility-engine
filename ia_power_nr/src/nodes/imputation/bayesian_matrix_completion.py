import pystan
import pandas as pd

from .matrix_completion import MatrixCompletion

SAMPLING_SEED = 100
N_CHAINS = 4


class BayesianMatrixCompletion(MatrixCompletion):
    """
    Used to run bayesian matrix completion using Stan.

    Parameters
    ----------
    stan_code: str
        Stan code for matrix completion
    scale_mean: bool
        If the data should be de-meaned before fitting
    scale_std: bool
        If the data should be be normalised to have a standard deviation of 1 before
        fitting

    Attributes
    ----------
    scaler: StandardScaler
        The sklearn scaler object to be used to scale the matrix values
    fitted: bool
        If the model has been fitted
    beneficiary_matrix: pd.DataFrame
        The dataframe used for fitting the Stan model. May have been scaled
    beneficiaries: List[str]
        list of beneficiary names
    demographics: List[str]
        list of demographics names
    n_latent_features: int
        The number of latent features that the model should fit
    """

    def __init__(self, stan_code, scale_mean, scale_std):
        self.stan_model = pystan.StanModel(model_code=stan_code)
        super().__init__(scale_mean, scale_std)

    def fit(self, beneficiary_matrix, n_latent_features):
        """
        Parameters
        ----------
        beneficiary_matrix: pd.DataFrame
            The matrix of beneficiary x demographics with missing values
        n_latent_features: int
            The number of latent features that the model should beneficiary_matrix

        Returns
        -------
        BayesianMatrixCompletion
            Self object with fitted
        """
        self.n_latent_features = n_latent_features
        beneficiary_matrix_scaled = self.scaler.fit_transform(beneficiary_matrix)
        beneficiary_matrix_scaled = pd.DataFrame(
            beneficiary_matrix_scaled,
            index=beneficiary_matrix.index,
            columns=beneficiary_matrix.columns,
        )
        super().fit(beneficiary_matrix_scaled)

        return self

    def sample(self, N_samples, sampler_control=None):
        """
        Return samples of completed matrices using the posterior distribution

        Parameters
        ----------
        N_samples: int
            The number of samples of fitted matrices to return
        sampler_control: dict
            A dictionary of parameters for the HMC/NUTS sampler

        Returns
        -------
        samples: List[pd.DataFrame]
            A list of beneficiary x demographics matrices.
        """
        super().sample(N_samples)

        model_data = _get_input_dictionary(
            self.beneficiary_matrix, self.n_latent_features
        )
        trace_matrix = self.stan_model.sampling(
            data=model_data,
            iter=N_samples,
            chains=N_CHAINS,
            seed=SAMPLING_SEED,
            control=sampler_control,
        )

        reconstructed_matrices = []
        for w, z in zip(trace_matrix.extract()["W"], trace_matrix.extract()["Z"]):
            sampled_matrix = z @ w.T
            sampled_matrix = pd.DataFrame(
                self.scaler.inverse_transform(z @ w.T),
                columns=self.demographics,
                index=self.beneficiaries,
            )
            reconstructed_matrices.append(sampled_matrix)

        return reconstructed_matrices[::-2]

    def __repr__(self):
        return (
            f"BayesianMatrixCompletion(latent_features: {self.n_latent_features},"
            f" fitted: {self.fitted})"
        )


def _get_input_dictionary(beneficiary_matrix, n_latent_features):
    """
    Create a dictionary of data elements required to fit the Stan model

    Parameters
    ----------
    beneficiary_matrix: pd.DataFrame
        A beneficiary x demographics matrix
    n_latent_features: int
        The number of latent features that the model should fit

    Returns
    -------
    mc_data: Dict
        A dictionary for data items for fitting the stan model
    """
    if n_latent_features > len(beneficiary_matrix.columns):
        raise ValueError("`n_latent_features` must be less than the numnber of columns")

    beneficiary_matrix.index.name = "beneficiary"
    matrix_long = _reshape_long_drop_nulls(beneficiary_matrix)

    mc_data = {
        "n_beneficiaries": beneficiary_matrix.shape[0],
        "n_demographics": beneficiary_matrix.shape[1],
        "n_features": n_latent_features,
        "n_entries": matrix_long.shape[0],
        "ii": matrix_long.beneficiary.astype("category").cat.codes.values + 1,
        "jj": matrix_long.demog.astype("category").cat.codes.values + 1,
        "demo_value": matrix_long.demo_value.values,
    }

    return mc_data


def _reshape_long_drop_nulls(beneficiary_matrix):
    """
    Reshape the matrix long and drop all rows where values is missing
    """
    matrix_long = beneficiary_matrix.melt(
        ignore_index=False, var_name="demog", value_name="demo_value"
    ).reset_index()

    matrix_long = matrix_long.loc[~matrix_long.demo_value.isna(), :]

    return matrix_long
