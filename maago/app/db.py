import duckdb
import os
import glob
from utils.normalization import get_normalised_date_value, get_normalised_bool_value, get_normalised_float_value, get_normalised_string_value
from utils.random import GetAlphaNumericString


class SingletonDuckDB:
    __instance = None

    @staticmethod
    def get_instance():
        if SingletonDuckDB.__instance == None:
            SingletonDuckDB()
        return SingletonDuckDB.__instance

    def __init__(self):
        if SingletonDuckDB.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            SingletonDuckDB.__instance = duckdb.connect(
                database=':memory:', read_only=False)
            SingletonDuckDB._migrate()

    @staticmethod
    def _migrate():
        instance = SingletonDuckDB.get_instance()
        # os.listdir('maago/database')
        sql_files = glob.glob("maago/database/migrations/*.sql")

        sql_files.sort()

        for file_path in sql_files:
            with open(file_path, 'r') as file:
                sql = file.read()
                instance.execute(sql)

    @staticmethod
    def cleanup():
        instance = SingletonDuckDB.get_instance()
        sql_files = glob.glob("maago/database/cleanup/*.sql")

        sql_files.sort()

        for file_path in sql_files:
            with open(file_path, 'r') as file:
                sql = file.read()
                instance.execute(sql)


def init_db():
    pass


def get_all_schemes():
    db = SingletonDuckDB.get_instance()
    return db.execute("SELECT * FROM schemes").fetchdf().to_dict('records')


def insert_scheme(data):
    db = SingletonDuckDB.get_instance()
    schemeID = GetAlphaNumericString(8)
    query = """
        INSERT INTO schemes
        (id, name, state,  department, description, inclusion_criteria, exclusion_criteria)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    # TODO: the field 'right' is not working for duckdb. Add it with another name
    db.execute(query, (
        schemeID,
        data['name'],
        data['state'],
        data['department'],
        data['description'],
        data['inclusion_criteria'],
        data['exclusion_criteria']
    ))
    return schemeID


def get_scheme(scheme_id):
    db = SingletonDuckDB.get_instance()
    scheme = db.execute(
        "SELECT * FROM schemes WHERE id = ?", (scheme_id,)
    ).fetchdf().to_dict('records')
    return scheme[0] if scheme else {}


def insert_location(location):
    db = SingletonDuckDB.get_instance()
    locationID = GetAlphaNumericString(8)
    query = """
        INSERT INTO locations
        (id, location_type, locality, pincode, ward_number, ward_name, village, survey_village_town_city) 
        VALUES ('%s', '%s', '%s', %s, %s, '%s', '%s', '%s')
    """
    db.sql(query % (
        locationID,
        location['areaType'],
        location['areaLocality'],
        location['pincode'],
        location['wardNumber'],
        location['wardName'],
        location['village'],
        location['surveyVillageTownCity']
    ))
    return locationID


def insert_family(family, locationID):
    db = SingletonDuckDB.get_instance()
    familyID = family['id']
    # import pdb
    # pdb.set_trace()
    query = """
        INSERT INTO families
        (id, location_id, caste, caste_category, pr_of_cg, has_residence_certificate, ration_card_type, ptgo_or_pvtg, are_forest_dwellers, has_phone, has_neighbourhood_phone_number)
        VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
    """
    db.sql(query % (
        familyID,
        locationID,
        family['caste'],
        family['casteCategory'],
        get_normalised_bool_value(family['prOfCG']),
        get_normalised_bool_value(family['hasResidenceCertificate']),
        family['rationCardType'],
        get_normalised_bool_value(family['ptgoOrPVTG']),
        get_normalised_bool_value(family['areForestDwellers']),
        get_normalised_bool_value(family['hasPhone']),
        get_normalised_bool_value(str(family['neighbourhoodPhone'] != ''))
    ))
    return familyID


def insert_family_member(member, familyID):
    db = SingletonDuckDB.get_instance()
    if 'name' not in member or not member['name']:
        return
    memberID = GetAlphaNumericString(8)
    query = """
        INSERT INTO family_members
        (id, family_id, name, dob, gender, family_role, disadvantaged, pregnancy, job, job_type, in_educational_institute, education_level, prev_year_tenth, prev_year_twelfth, tenth_percentage_marks, twelfth_percentage_marks, tenth_top_ten, twelfth_top_ten, has_bocw_card, bocw_card_issue_date, has_uow_card, uow_card_issue_date)
        VALUES ('%s', '%s', '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, %s, '%s', '%s', '%s', %s, '%s', %s)
    """
    db.sql(query % (
        memberID,
        familyID,
        member['name'],
        get_normalised_date_value(member['dob']),
        get_normalised_string_value(member['gender']),
        member['familyRole'],
        get_normalised_bool_value(member['disadvantaged']),
        get_normalised_bool_value(member['pregnancy']),
        member['job'],
        member['jobType'],
        get_normalised_bool_value(member['inEducationalInstitute']),
        member['educationLevel'],
        get_normalised_bool_value(member['prevYearTenth']),
        get_normalised_bool_value(member['prevYearTwelfth']),
        get_normalised_float_value(member['tenthPercentageMarks']),
        get_normalised_float_value(member['twelfthPercentageMarks']),
        get_normalised_bool_value(member['tenthTopTen']),
        get_normalised_bool_value(member['twelfthTopTen']),
        get_normalised_bool_value(member['hasBOCWCard']),
        get_normalised_date_value(member['bocwCardIssueDate']),
        get_normalised_bool_value(member['hasUOWCard']),
        get_normalised_date_value(member['uowCardIssueDate'])
    ))
    return memberID


def execute_custom_query(query):
    db = SingletonDuckDB.get_instance()
    print(query)
    res = db.sql(query)
    return res.fetchdf()
