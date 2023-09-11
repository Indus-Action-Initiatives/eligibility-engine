from abc import abstractmethod
from app.db import execute_custom_query
from loaders.beneficiary_scheme_mapping import get_criteria, df_to_dict
from utils.proximity_score import populateProximityScores


PROXIMITY_SCORE_KEY = "proximity_score"


class ProjectLoader:
    def __init__(self) -> None:
        self.beneficiaries = None
        self.schemes = None

    @abstractmethod
    def load_beneficiaries(self, beneficiaries):
        pass

    @abstractmethod
    def load_schemes(self, schemes):
        pass

    @abstractmethod
    def generate_eligibility_query(self):
        pass

    @abstractmethod
    def execute_custom_query(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    def __get_scheme_auxilliary_columns(self, scheme):
        acKeysFromScheme = [key for key in scheme.keys() if "auxilliary" in key]
        auxilliaryColumns = {
            key.split("_")[1]: scheme[key] for key in acKeysFromScheme if scheme[key]
        }

        return auxilliaryColumns

    # def __get_criteria(self, scheme):
    #     inclusionCriteria = scheme["inclusion_criteria"]
    #     criteria = getCriteriaTokensFromInclusionCriteria(inclusionCriteria)
    #     # TODO: Add exclusion criteria
    #     criteriaColumns = {}
    #     for i, c in enumerate(criteria):
    #         criteriaColumns["criteria%d" % i] = getColumnsFromCriterion(c)
    #     # Criteria
    #     criteriaStrings = [
    #         "CASE WHEN %s THEN 1 ELSE 0 END as 'criteria%d'" % (c, i)
    #         for i, c in enumerate(criteria)
    #     ]
    #     return criteriaColumns, criteriaStrings

    # This method must be called only when the schemes and the beneficiaries are loaded to the in-memory database
    def get_beneficiary_scheme_mapping(self):
        assert self.beneficiaries != None
        assert self.schemes != None

        orderedColumns = []
        schemeBeneficiariesRows = []
        schemeBeneficiaries = {}
        criteriaColumns = {}
        for scheme in self.schemes:
            auxilliaryColumns = self.__get_scheme_auxilliary_columns(scheme)
            criteriaColumns, criteriaStrings = get_criteria(scheme)
            eligibilityQuery, orderedColumnNames = self.generate_eligibility_query(
                scheme, auxilliaryColumns, criteriaStrings
            )
            orderedColumns = orderedColumnNames
            # Execute eligibility query
            schemeBeneficiariesDF = self.execute_custom_query(eligibilityQuery)
            rows = df_to_dict(schemeBeneficiariesDF)
            for r in rows:
                schemeBeneficiariesRows.append(r)

            populateProximityScores(
                schemeBeneficiaries, rows, orderedColumns, criteriaColumns
            )
        return schemeBeneficiaries

    # # this method must be called only after the beneficiaries and the schemes are loaded
    # def populate_proximity_scores(self, criteriaColumns):
    #     assert self.beneficiaries != None
    #     assert self.schemes != None

    #     schemeBeneficiaries = {}

    #     for row in self.beneficiaries:
    #         beneficiaryKey = "%s__%s" % (row["f.id"], row["fm.id"])
    #         schemeName = row["scheme_name"]
    #         beneficiary = {}
    #         if beneficiaryKey in schemeBeneficiaries:
    #             beneficiary = schemeBeneficiaries[beneficiaryKey]
    #         for i, (key, v) in enumerate(row.items()):
    #             if "criteria" not in key:
    #                 beneficiary[key] = row[key]
    #             else:
    #                 # TODO: Add description of the criteria as well.
    #                 beneficiary["%s__%s" % (schemeName, key)] = row[key]
    #         if row["main_criteria"] == 1:
    #             beneficiary["%s__%s" % (schemeName, PROXIMITY_SCORE_KEY)] = 1
    #         else:
    #             beneficiary[
    #                 "%s__%s" % (schemeName, PROXIMITY_SCORE_KEY)
    #             ] = calculateProximityScore(row, criteriaColumns)
    #         schemeBeneficiaries[beneficiaryKey] = beneficiary
