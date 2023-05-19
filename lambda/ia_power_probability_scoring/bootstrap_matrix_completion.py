"""Bootstrap matrix completion method"""

# from src.nodes.imputation.matrix_completion import MatrixCompletion
from matrix_completion import MatrixCompletion
from sklearn.utils import resample
import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import SimpleImputer, IterativeImputer, KNNImputer


class BootstrapMatrixCompletion(MatrixCompletion):
    """
    Used to run Boostrapped Matrix Completion.

    Parameters
    ----------
    numeric_imputer: str
        Numeric imputer type to use - "simple" or "iterative"
    categorical_imputer: str
        Categorical imputer type to use - "most_frequent" or "knn"
    scale_mean: bool
        If the data should be de-meaned before fitting
    scale_std: bool
        If the data should be normalised to have a s.d. of 1 before fitting
    raise_if_all_missing: bool
        Whether to raise error if there are columns with no data. If not, the
        columns are dropped.

    Attributes
    ----------
    scaler: StandardScaler
        The sklearn scaler object to be used to scale the matrix values
    fitted: bool
        If the model has been fitted
    beneficiary_matrix: pd.DataFrame
        The dataframe used for imputation. May have been scaled
    beneficiaries: List[str]
        list of beneficiary names
    demographics: List[str]
        list of demographics names
    """

    def __init__(
        self,
        numeric_imputer,
        categorical_imputer,
        scale_mean,
        scale_std,
        raise_if_all_missing,
    ):
        super().__init__(scale_mean, scale_std, raise_if_all_missing)

        if numeric_imputer == "iterative":
            self.n_imputer = IterativeImputer(
                random_state=0,
                max_iter=20,
                initial_strategy="mean",
                skip_complete=True,
            )
        elif numeric_imputer == "simple":
            self.n_imputer = SimpleImputer()
        else:
            raise NotImplementedError(
                "numeric_imputer must be either 'simple' or 'iterative'"
            )

        if categorical_imputer == "most_frequent":
            self.c_imputer = SimpleImputer(strategy="most_frequent")
        elif categorical_imputer == "knn":
            self.c_imputer = KNNImputer()
        else:
            raise NotImplementedError(
                "categorical_imputer must be either 'knn' or 'most_frequent'"
            )

    def fit(self, beneficiary_matrix, numeric_cols, categorical_cols):
        """
        Prepare the beneficiary data by scaling down numeric information and
        ordinal-ly encoding the categorical variables.

        Parameters
        ----------
        beneficiary_matrix : pd.DataFrame
            Beneficiary data frame with missing values to be imputed.
        numeric_cols: list[str]
            List of numeric column names
        categorical_cols: list[str]
            List of categorical column names

        Returns
        -------
        BootstrapMatrixCompletion
            Self object fitted.

        """
        self.numeric_cols = numeric_cols
        self.categorical_cols = categorical_cols
        super().fit(beneficiary_matrix)

        if any(self.full_missing_variables):
            beneficiary_matrix = beneficiary_matrix.loc[:, ~self.full_missing_variables]
            self.numeric_cols = [
                col for col in self.numeric_cols if not self.full_missing_variables[col]
            ]
            self.categorical_cols = [
                col
                for col in self.categorical_cols
                if not self.full_missing_variables[col]
            ]

        self.beneficiary_matrix_prep = beneficiary_matrix.copy()
        
        print(beneficiary_matrix.dtypes)
        print(self.numeric_cols)
        

        # Scale numeric data
        self.beneficiary_matrix_prep[self.numeric_cols] = self.scaler.fit_transform(
            self.beneficiary_matrix_prep[self.numeric_cols].astype("float")
        )
        # One-hot-encode categorical data
        self.beneficiary_matrix_prep = pd.get_dummies(
            self.beneficiary_matrix_prep,
            columns=self.categorical_cols,
            prefix_sep="_c_",
            dummy_na=True,
            drop_first=True,
        )
        self.dummy_cat_cols = []
        for col in self.categorical_cols:
            nan_col = col + "_c_nan"
            cols = [
                name
                for name in self.beneficiary_matrix_prep.columns
                if name.startswith(col) and name != nan_col
            ]
            self.beneficiary_matrix_prep.loc[
                self.beneficiary_matrix_prep[nan_col] == 1, cols
            ] = np.nan
            self.beneficiary_matrix_prep = self.beneficiary_matrix_prep.drop(
                columns=nan_col
            )
            self.dummy_cat_cols = self.dummy_cat_cols + cols
        return self

    def sample(self, N_samples):
        """
        Run imputation on bootstrapped samples and impute over N_samples.

        Imputation is first done for categorical features. Then categorical variables
        are one-hot-encoded and numerical features are imputed. Finally dataset is
        scaled up and one-hot-decoded.

        Parameters
        ----------
        N_samples : int
            Number of bootstrapped samples to create.

        Returns
        -------
        df_collection : list[pd.DataFrame]
            List of bootstrapped and imputed beneficiary data.

        """
        super().sample(N_samples)

        df_collection = []

        for sample in range(N_samples):

            df = self.beneficiary_matrix_prep.copy()

            df_sampled = resample(
                df,
                n_samples=len(self.beneficiaries),
                stratify=SimpleImputer(strategy="most_frequent").fit_transform(
                    df[self.dummy_cat_cols]
                ),
            )  # stratify specification can't have NaNs

            self.n_imputer.fit(df_sampled)
            self.c_imputer.fit(df_sampled)

            num_imputed = pd.DataFrame(
                self.n_imputer.transform(df),
                index=df.index,
                columns=df.columns,
            )
            cat_imputed = pd.DataFrame(
                self.c_imputer.transform(df),
                index=df.index,
                columns=df.columns,
            )
            df[self.numeric_cols] = num_imputed[self.numeric_cols]
            df[self.dummy_cat_cols] = cat_imputed[self.dummy_cat_cols]

            # # Inverse transform the numeric scaling
            df[self.numeric_cols] = self.scaler.inverse_transform(df[self.numeric_cols])

            # Inverse transform the one-hot-encoding
            beneficiary_matrix_final = undummify(df, prefix_sep="_c_")

            df_collection.append(beneficiary_matrix_final)

        return df_collection

    def __repr__(self):
        return f"BootstrapMatrixCompletion(" f" fitted: {self.fitted})"


def undummify(df, prefix_sep):
    """
    Un-dummify the one-hot-encoded dataframe generated by pd.get_dummies()

    Parameters
    ----------
    df : pd.DataFrame
        Dummified, one-hot-encoded dataframe.
    prefix_sep : str
        Separation character used for OHE column names.

    Returns
    -------
    undummified_df : pd.DataFrame
        Un-dummified dataframe.

    """
    cols2collapse = {
        item.split(prefix_sep)[0]: (prefix_sep in item) for item in df.columns
    }
    series_list = []
    for col, needs_to_collapse in cols2collapse.items():
        if needs_to_collapse:
            undummified = (
                df.filter(like=col)
                .idxmax(axis=1)
                .apply(lambda x: x.split(prefix_sep, maxsplit=1)[1])
                .rename(col)
            )
            series_list.append(undummified)
        else:
            series_list.append(df[col])
    undummified_df = pd.concat(series_list, axis=1)
    return undummified_df
