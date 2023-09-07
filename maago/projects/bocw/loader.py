from loaders.config_loaders import get_config_mappings
from ..loader import ProjectLoader
from datetime import datetime
from utils.dictionary import getMappedDict, splitCombinedDict
from utils.beneficiary_utils import fuzzy_matching
from utils.re_utils import getOrderedColumnNamesFromTheSelectClause
from utils.csv import CSVLoader
from projects.bocw.db.db import BoCWSingletonDuckDB
from utils.random import GetAlphaNumericString
from utils.normalization import (
    get_normalised_bool_value,
    get_normalised_date_value,
    get_normalised_string_value,
    get_normalised_float_value,
)

config = get_config_mappings()

UNKNOWN_SCORE = 0.001
UNKNOWN_STRING = "unknown"
UNKNOWN_NUMBER = -19
UNKNOWN_DATE = datetime.strptime("30-08-1857", "%d-%m-%Y")
PROXIMITY_SCORE_KEY = "proximity_score"


class BOCWLoader(ProjectLoader):
    def __insert_beneficiary(self, member):
        db = BoCWSingletonDuckDB.get_instance()
        memberID = member["id"]
        query = """
            INSERT INTO family_members
            (id, age, gender, occupation, marital_status, pregnancy_status, bocw_card_registration_date, health_status, number_of_children, children_school_or_college, spouse_alive, occupation_of_surviving_spouse, receiving_pension, receiving_government_aid, home_ownership_status)
            VALUES ('%s', %d, '%s', '%s', '%s', '%s', %s, '%s', %d, '%s', '%s', '%s', '%s', '%s', '%s')
        """
        query = query % (
            memberID,
            member["age"],
            get_normalised_string_value(member["gender"]),
            get_normalised_string_value(member["occupation"]),
            get_normalised_string_value(member["marital_status"]),
            get_normalised_string_value(member["pregnancy_status"]),
            get_normalised_date_value(member["bocw_card_registration_date"]),
            get_normalised_string_value(member["health_status"]),
            member["number_of_children"],
            get_normalised_string_value(member["children_school_or_college"]),
            get_normalised_bool_value(member["spouse_alive"]),
            get_normalised_string_value(member["occupation_of_surviving_spouse"]),
            get_normalised_bool_value(member["receiving_pension"]),
            get_normalised_bool_value(member["receiving_government_aid"]),
            get_normalised_string_value(member["home_ownership_status"]),
        )
        db.sql(query)
        return memberID

    def load_schemes(self):
        schemes = CSVLoader("maago/projects/bocw/config/schemes.csv")
        self.schemes = schemes

    def load_beneficiaries(self, beneficiaries):
        super().load_beneficiaries(beneficiaries)

        for beneficiary in beneficiaries:
            self.__insert_beneficiary(beneficiary)

        self.beneficiaries = beneficiaries

    def generate_eligibility_query(self, scheme, auxilliaryColumns, criteriaStrings):
        mainCriteriaString = (
            "(CASE WHEN %s THEN 1 ELSE 0 END) as 'main_criteria'"
            % scheme["inclusion_criteria"]
        )

        # from
        fromClause = "FROM family_members as fm"

        # TODO: This is ugly, bad, nasty. Need to do a better job with this.
        # construct select clause
        selectClause = """SELECT \'%s\' as \'scheme_name\', \'%s\' as \'scheme_id\',
                fm.id as \'fm.id\', fm.age as \'fm.age\', fm.gender as \'fm.gender\', fm.occupation as \'fm.occupation\', fm.marital_status as \'fm.marital_status\',
                fm.pregnancy_status as \'fm.pregnancy_status\', fm.bocw_card_registration_date as \'fm.bocw_card_registration_date\', fm.health_status as \'fm.health_status\', fm.number_of_children as \'fm.number_of_children\',
                fm.children_school_or_college as \'fm.children_school_or_college\', fm.spouse_alive as \'fm.spouse_alive\', fm.occupation_of_surviving_spouse as \'fm.occupation_of_surviving_spouse\',
                fm.receiving_pension as \'fm.receiving_pension\', fm.receiving_government_aid as \'fm.receiving_government_aid\', fm.home_ownership_status as \'fm.home_ownership_status\',
                """ % (
            scheme["name"],
            scheme["id"],
        ) + ", ".join(
            ["(%s) as '%s'" % (auxilliaryColumns[k], k) for k in auxilliaryColumns]
        )

        # get values for each part of the select clause
        orderedColumnNames = getOrderedColumnNamesFromTheSelectClause(selectClause)

        # if auxilliary columns wrap the main query with a CTE
        if auxilliaryColumns:
            selectClause = "WITH cte_query AS (%s) SELECT " % (
                selectClause + " " + fromClause
            )
            selectClause += ", ".join(
                ["\"%s\" as '%s'" % (c, c) for c in orderedColumnNames]
            )
            selectClause += ", "
            fromClause = "FROM cte_query"
            # TODO: quote the columns in where clause in case of auxilliary columns

        selectClause += ", ".join(criteriaStrings) + ", " + mainCriteriaString

        eligibilityQuery = selectClause + " " + fromClause

        return eligibilityQuery, orderedColumnNames

    def cleanup(self):
        super().cleanup()
        BoCWSingletonDuckDB.cleanup()
        return

    def execute_custom_query(self, query):
        db = BoCWSingletonDuckDB.get_instance()
        print(query + "\n\n")
        res = db.sql(query)
        return res.fetchdf()
