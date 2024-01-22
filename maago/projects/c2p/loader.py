from ..loader import ProjectLoader
from datetime import datetime
from projects.c2p.db.db import C2PSingletonDuckDB
from utils.csv import CSVLoader
from utils.normalization import (
    get_normalised_date_value,
    get_normalised_float_value,
    get_normalised_string_value,
    get_normalised_bool_value
)
from utils.re_utils import getOrderedColumnNamesFromTheSelectClause

UNKNOWN_SCORE = 0.001
UNKNOWN_STRING = "unknown"
UNKNOWN_NUMBER = -19
UNKNOWN_DATE = datetime.strptime("30-08-1857", "%d-%m-%Y")
PROXIMITY_SCORE_KEY = "proximity_score"

class C2PLoader(ProjectLoader):
    def load_schemes(self):
        schemes = CSVLoader("projects/c2p/config/schemes.csv")
        self.schemes = schemes

    def __new_family(self, beneficiary):
        return beneficiary
    
    def __insert_family(self, family):
        db = C2PSingletonDuckDB.get_instance()
        familyID = family["id"]
        query = """
            INSERT INTO families
            (id, annual_income, por)
            VALUES ('%s', '%s', '%s')
        """
        db.sql(
            query
            % (
                familyID,               
                get_normalised_float_value(family["annual_income"]),
                get_normalised_string_value(family["place_of_residence"])
            )
        )
        return familyID
    
    def __check_and_return(self, obj, key):
        keys = obj.keys()
        if key not in keys:
            return None
        else:
            return obj[key]
        
    def __get_list_values_string(values):
        ret_val = "list_value("
        if values is None:
            ret_val = ret_val + ")"
        else:
            ret_val = ret_val + ', '.join(f"'{v}'" for v in values) + ")"

        return ret_val

    def __insert_family_member(self, family_member, familyID):        
        # get common properties
        id = family_member["id"]
        family_id = family_member["family_id"]
        name = family_member["name"]
        dob = family_member["dob"]

        # get bocw properties        
        occupation = self.__check_and_return(family_member, "occupation")
        labour_card_status = self.__check_and_return(family_member, "labour_card_status")
        renewal_date = self.__check_and_return(family_member, "renewal_date")
        marital_status = self.__check_and_return(family_member, "marital_status")
        wife_or_cw_pregnant = self.__check_and_return(family_member, "wife_or_cw_pregnant")
        pregnancy_status = self.__check_and_return(family_member, "pregnancy_status")
        have_children = self.__check_and_return(family_member, "have_children")
        children_school = self.__check_and_return(family_member, "children_school")
        children_college = self.__check_and_return(family_member, "children_college")
        received_benefits = self.__check_and_return(family_member, "received_benefits")

        # get pmmvy properties
        last_child_270_days = self.__check_and_return(family_member, "last_child_270_days")
        dsw = self.__check_and_return(family_member, "dsw")

        # get rte properties
        gender = self.__check_and_return(family_member, "gender")
        child_class = self.__check_and_return(family_member, "class")

        db = C2PSingletonDuckDB.get_instance()
        query = """
            INSERT INTO family_members
            (id, family_id, name, dob, occupation, labour_card_status, renewal_date, marital_status, wife_or_cw_pregnant,
            pregnancy_status, have_children, children_school, children_college, received_benefits, last_child_270_days,
            dsw, gender, class)
            VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, '%s', %s, '%s', '%s')
        """
        db.sql(
            query
            % (
                id,
                family_id,
                name,
                get_normalised_date_value(dob),
                get_normalised_string_value(occupation),
                get_normalised_string_value(labour_card_status),
                get_normalised_date_value(renewal_date),
                get_normalised_string_value(marital_status),
                get_normalised_bool_value(wife_or_cw_pregnant),
                get_normalised_string_value(pregnancy_status),
                get_normalised_bool_value(have_children),
                get_normalised_string_value(children_school),
                get_normalised_string_value(children_college),
                self.__get_list_values_string(received_benefits),
                get_normalised_string_value(last_child_270_days),
                self.__get_list_values_string(dsw),
                get_normalised_string_value(gender),
                get_normalised_string_value(child_class)
            )
        )

        return id

    def __load_beneficiary_to_db(self, beneficiary):
        familyID = self.__insert_family(beneficiary["household"])
        for bocw_member in beneficiary["bocw"]:
            self.__insert_family_member(bocw_member, familyID)
        for pregnant_member in beneficiary["pmmvy"]:
            self.__insert_family_member(pregnant_member, familyID)
        for child_member in beneficiary["rte"]:
            self.__insert_family_member(child_member, familyID)

    def load_beneficiaries(self, beneficiaries):
        super().load_beneficiaries(beneficiaries)

        families = []
        # for each beneficiary, create a structured (family) object out of it divided as family, respondent and family member data
        for beneficiary in beneficiaries:
            # for each beneficiary row construct a family object
            family = self.__new_family(beneficiary)
            self.__load_beneficiary_to_db(family)
            families.append(family)

        self.beneficiaries = families

    def generate_eligibility_query(self, scheme, auxilliaryColumns, criteriaStrings):
        mainCriteriaString = (
            "(CASE WHEN %s THEN 1 ELSE 0 END) as 'main_criteria'"
            % scheme["inclusion_criteria"]
        )

        # from
        fromClause = (
            "FROM families as f INNER JOIN family_members as fm ON f.id = fm.family_id"
        )

        # TODO: This is ugly, bad, nasty. Need to do a better job with this.
        # construct select clause
        selectClause = """SELECT \'%s\' as \'scheme_name\',
                f.id as \'f.id\', f.por as \'f.por'\, f.annual_income as \'f.annual_income'\,
                fm.id as \'fm.id\', fm.name as \'fm.name\', fm.dob as \'fm.dob\', fm.gender as \'fm.gender\',
                fm.occupation as \'fm.occupation'\, fm.labour_card_status as \'fm.labour_card_status'\,
                fm.renewal_date as \'fm.renewal_date'\, fm.marital_status as \'fm.marital_status'\,
                fm.wife_or_cw_pregnant as \'fm.wife_or_cw_pregnant'\, fm.pregnancy_status as \'fm.pregnancy_status'\,
                fm.have_children as \'fm.have_children'\, fm.children_school as \'fm.children_school'\,
                fm.children_college as \'fm.children_college'\, fm.received_benenfits as \'fm.received_benefits'\,
                fm.last_child_270_days as \'fm.last_child_270_days'\, fm.dsw as \'fm.dsw'\,
                fm.class as \'fm.class'\,
                """ % scheme[
            "name"
        ]

        # get values for each part of the select clause
        orderedColumnNames = getOrderedColumnNamesFromTheSelectClause(selectClause)

        selectClause += ", ".join(criteriaStrings) + ", " + mainCriteriaString

        eligibilityQuery = selectClause + " " + fromClause

        return eligibilityQuery, orderedColumnNames


    def cleanup(self):
        super().cleanup()
        C2PSingletonDuckDB.cleanup()
        return

    def execute_custom_query(self, query):
        db = C2PSingletonDuckDB.get_instance()
        # print(query + "\n\n")
        res = db.sql(query)
        return res.fetchdf()
    
    def reset():
        C2PSingletonDuckDB.reset()

    execute_custom_query.callback = reset
    __insert_family.callback = reset
    __insert_family_member.callback = reset