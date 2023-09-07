from loaders.config_loaders import get_config_mappings
from ..loader import ProjectLoader
from datetime import datetime
from utils.dictionary import getMappedDict, splitCombinedDict
from utils.beneficiary_utils import fuzzy_matching
from utils.re_utils import getOrderedColumnNamesFromTheSelectClause
from utils.csv import CSVLoader
from projects.cg_rte_plus.db.db import CGRTEPlusSingletonDuckDB
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


class CGRTEPlusLoader(ProjectLoader):
    def __determine_respondent_role(respondent, parentFound):
        if parentFound:
            return "child"
        elif respondent["gender"] == "male":
            return "father"
        elif respondent["gender"] == "female":
            return "mother"
        return UNKNOWN_STRING

    def __determine_family_roles(self, family) -> bool:
        parentFound = False
        for i, member in enumerate(family["members"]):
            if "relationshipWithRespondent" not in member:
                continue
            memberRole, parent = self.__determine_family_member_role(member)
            parentFound = parent
            member["familyRole"] = memberRole
            if member["relationshipWithRespondent"] == "husband" and parent:
                member["familyRole"] = "father"
            elif member["relationshipWithRespondent"] == "wife" and parent:
                member["familyRole"] = "mother"

        return parentFound

    def __determine_family_member_role(self, member):
        relationshipWithRespondent = member["relationshipWithRespondent"]
        # TODO: Replace with match-case in py 3.10
        if relationshipWithRespondent == "father":
            return "father", True
        elif relationshipWithRespondent == "mother":
            return "mother", True
        elif relationshipWithRespondent in ["child", "brother", "sister", "sibling"]:
            return "child", False
        elif "inlaw" in relationshipWithRespondent.replace("-", "").lower():
            return "in-law", False
        elif relationshipWithRespondent in ["", "other"]:
            return "other", False
        return UNKNOWN_STRING, False

    def __populate_pregnancy_status(self, family, beneficiary):
        # get the names of the pregnant women of the family from the pregnancy mapping
        pregnantWomenCombinedDict = getMappedDict(
            config["pregnancyMapping"], beneficiary
        )
        # current data has a provision of only two pregnant women, so pass two
        pregnantWomen = splitCombinedDict(pregnantWomenCombinedDict, 2)

        for woman in pregnantWomen:
            if "name" not in woman:
                return
            name = woman["name"].strip()
            if name == "":
                return
            fuzzyScore, index = fuzzy_matching(name, family["members"])
            if index >= 0 and index < (len(family["members"]) - 1):
                family["members"][index]["pregnancy"] = "yes"
            # elif index == (len(family['members']) - 1):
            #     respondent['pregnancy'] = 'yes'
        for member in family["members"]:
            if member["gender"] == "male":
                member["pregnancy"] = "no"
            elif "pregnancy" not in member or member["pregnancy"] == "":
                member["pregnancy"] = UNKNOWN_STRING

    def __new_family(self, beneficiary):
        family = beneficiary

        # transformations & addition of attributes
        parentFound = self.__determine_family_roles(family)
        self.__populate_pregnancy_status(family, beneficiary)

        return family

    def __insert_location(self, location):
        db = CGRTEPlusSingletonDuckDB.get_instance()
        locationID = GetAlphaNumericString(8)
        query = """
            INSERT INTO locations
            (id, location_type, locality, pincode, ward_number, ward_name, village, survey_village_town_city) 
            VALUES ('%s', '%s', '%s', %s, %s, '%s', '%s', '%s')
        """
        db.sql(
            query
            % (
                locationID,
                location["areaType"],
                location["areaLocality"],
                location["pincode"],
                location["wardNumber"],
                location["wardName"],
                location["village"],
                location["surveyVillageTownCity"],
            )
        )
        return locationID

    def __insert_family(self, family, locationID):
        db = CGRTEPlusSingletonDuckDB.get_instance()
        familyID = family["id"]
        query = """
            INSERT INTO families
            (id, location_id, caste, caste_category, pr_of_cg, has_residence_certificate, ration_card_type, ptgo_or_pvtg, are_forest_dwellers, has_phone, has_neighbourhood_phone_number)
            VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
        """
        db.sql(
            query
            % (
                familyID,
                locationID,
                family["caste"],
                family["casteCategory"],
                get_normalised_bool_value(family["prOfCG"]),
                get_normalised_bool_value(family["hasResidenceCertificate"]),
                family["rationCardType"],
                get_normalised_bool_value(family["ptgoOrPVTG"]),
                get_normalised_bool_value(family["areForestDwellers"]),
                get_normalised_bool_value(family["hasPhone"]),
                get_normalised_bool_value(str(family["neighbourhoodPhone"] != "")),
            )
        )
        return familyID

    def __insert_family_member(self, member, familyID):
        db = CGRTEPlusSingletonDuckDB.get_instance()
        if "name" not in member or not member["name"]:
            return
        memberID = GetAlphaNumericString(8)
        query = """
            INSERT INTO family_members
            (id, family_id, name, dob, gender, family_role, disadvantaged, pregnancy, job, job_type, in_educational_institute, education_level, prev_year_tenth, prev_year_twelfth, tenth_percentage_marks, twelfth_percentage_marks, tenth_top_ten, twelfth_top_ten, has_bocw_card, bocw_card_issue_date, has_uow_card, uow_card_issue_date)
            VALUES ('%s', '%s', '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, %s, '%s', '%s', '%s', %s, '%s', %s)
        """
        db.sql(
            query
            % (
                memberID,
                familyID,
                member["name"],
                get_normalised_date_value(member["dob"]),
                get_normalised_string_value(member["gender"]),
                member["familyRole"],
                get_normalised_bool_value(member["disadvantaged"]),
                get_normalised_bool_value(member["pregnancy"]),
                member["job"],
                member["jobType"],
                get_normalised_bool_value(member["inEducationalInstitute"]),
                member["educationLevel"],
                get_normalised_bool_value(member["prevYearTenth"]),
                get_normalised_bool_value(member["prevYearTwelfth"]),
                get_normalised_float_value(member["tenthPercentageMarks"]),
                get_normalised_float_value(member["twelfthPercentageMarks"]),
                get_normalised_bool_value(member["tenthTopTen"]),
                get_normalised_bool_value(member["twelfthTopTen"]),
                get_normalised_bool_value(member["hasBOCWCard"]),
                get_normalised_date_value(member["bocwCardIssueDate"]),
                get_normalised_bool_value(member["hasUOWCard"]),
                get_normalised_date_value(member["uowCardIssueDate"]),
            )
        )
        return memberID

    def __load_beneficiary_to_db(self, beneficiary):
        location = beneficiary["location"]
        if location["pincode"] == "":
            location["pincode"] = "0"
        if location["wardNumber"] == "":
            location["wardNumber"] = "0"
        locationID = self.__insert_location(location)
        familyID = self.__insert_family(beneficiary, locationID)
        for member in beneficiary["members"]:
            self.__insert_family_member(member, familyID)

    def load_schemes(self):
        schemes = CSVLoader("maago/projects/cg_rte_plus/config/schemes.csv")
        self.schemes = schemes

    def load_beneficiaries(self, beneficiaries):
        super().load_beneficiaries(beneficiaries)

        families = []
        # For each beneficiary, create a structured (family) object out of it divided as family, respondent and family member data
        for beneficiary in beneficiaries:
            # For each beneficiary row construct a family object
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
                f.id as \'f.id\', f.caste as \'f.caste\', f.caste_category as \'f.caste_category\', f.pr_of_cg as \'f.pr_of_cg\', 
                f.has_residence_certificate as \'f.has_residency_certificate\', f.ration_card_type as \'f.ration_card_type\',
                f.ptgo_or_pvtg as \'f.ptgo_or_pvtg\', f.are_forest_dwellers as \'f.are_forest_dwellers\', f.has_phone as \'f.has_phone\',
                f.has_neighbourhood_phone_number as \'f.has_neighbourhood_phone_number\',
                fm.id as \'fm.id\', fm.name as \'fm.name\', fm.dob as \'fm.dob\', fm.gender as \'fm.gender\', fm.family_role as \'fm.family_role\', fm.disadvantaged as \'fm.disadvantaged\',
                fm.job as \'fm.job\', fm.job_type as \'fm.job_type\', fm.in_educational_institute as \'fm.in_educational_institute\', fm.education_level as \'fm.education_level\',
                fm.prev_year_tenth as \'fm.prev_year_tenth\', fm.prev_year_twelfth as \'fm.prev_year_twelfth\', fm.tenth_percentage_marks as \'fm.tenth_percentage_marks\',
                fm.twelfth_percentage_marks as \'fm.twelfth_percentage_marks\', fm.tenth_top_ten as \'fm.tenth_top_ten\', fm.twelfth_top_ten as \'fm.twelfth_top_ten\',
                fm.has_bocw_card as \'fm.has_bocw_card\', fm.bocw_card_issue_date as \'fm.bocw_card_issue_date\', fm.has_uow_card as \'fm.has_uow_card\', fm.uow_card_issue_date as \'fm.uow_card_issue_date\',
                fm.pregnancy as \'fm.pregnancy\',          
                """ % scheme[
            "name"
        ] + ", ".join(
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
        CGRTEPlusSingletonDuckDB.cleanup()
        return

    def execute_custom_query(self, query):
        db = CGRTEPlusSingletonDuckDB.get_instance()
        print(query + "\n\n")
        res = db.sql(query)
        return res.fetchdf()
