from src.utils import load_params_file
from src.nodes.transforms import transforms
import src.nodes.load_data as ld
from src.utils import save_output

bocw_benefit_map = {
    "Maternity.*": "BoCW Maternity benefits",
    ".*Edu.*": "BoCW Financial assistance for education",
    ".*Marriage": "BoCW Financial assistance for marriage of children",
    "Pension.*": "BoCW Pension benefit",
    "^Death$": "BoCW Death benefit",
    "Death & Funeral": "BoCW Death benefit",
}


def get_bocw_beneficiary(params=None):

    """
    Extract BoCW raw data set
    Transform into beneficiary columns
    Write /return output indexed by registration number

    Parameters
    ----------
    params : dict, optional
        by default None

    Returns
    -------
    pd.DataFrame
        output dataframe with transformed bocw columns
    """

    if not params:
        params = load_params_file()
    columns = params["bocw_useful_columns"] + ["Registration No"]
    mapping = params["bocw_target_columns"]
    bocw = ld.load_generic_data("bocw")

    transformed_df = transforms.bocw_transform(bocw[columns], columns, mapping)
    return transformed_df


def get_bocw_claims():
    """
    Load and process BoCW claims data.
    Column names and indices are set, and multiple schemes collapsed.

    Returns
    -------
    df_claims_combined : pd.DataFrame
        Claims made by beneficiaries, identified by registration number.

    """
    bocw_claims_data = ld.load_generic_data("bocw_claims_raw")
    bocw_claims_data.columns = bocw_claims_data.iloc[0]

    df_claims = bocw_claims_data[["Reg. No.", "Benefit"]].loc[
        1:,
    ]
    df_claims["scheme"] = df_claims.Benefit.replace(bocw_benefit_map, regex=True)
    df_claims.drop_duplicates(subset=["Reg. No.", "scheme"], inplace=True)
    df_claims = df_claims.rename(columns={"Reg. No.": "beneficiary_name"})
    df_claims_combined = (
        df_claims.groupby(["beneficiary_name"])["scheme"]
        .apply(lambda x: ",".join(x))
        .reset_index()
    )
    return df_claims_combined


if __name__ == "__main__":
    # usage
    save_output("bocw_reg_trans")(get_bocw_beneficiary)()
    save_output("bocw_claims_trans")(get_bocw_claims)()
