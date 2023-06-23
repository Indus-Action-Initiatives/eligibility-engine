import duckdb
from utils.random import GetAlphaNumericString


db = duckdb.connect(':memory:')

db.execute("""
    CREATE TABLE IF NOT EXISTS schemes(
        id INTEGER,
        name VARCHAR,
        state VARCHAR,
        department VARCHAR,
        description VARCHAR,
        inclusion_criteria VARCHAR,
        exclusion_criteria VARCHAR
    )
""")


def init_db():
    pass


def get_all_schemes():
    return db.execute("SELECT * FROM schemes").fetchdf().to_dict('records')


def insert_scheme(data):
    query = """
        INSERT INTO schemes (name, state,  department, description, inclusion_criteria, exclusion_criteria)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    db.execute(query, (
        data['name'],
        data['state'],
        data['department'],
        data['description'],
        data['inclusion_criteria'],
        data['exclusion_criteria']
    ))


def get_scheme(scheme_id):
    scheme = db.execute(
        "SELECT * FROM schemes WHERE id = ?", (scheme_id,)
    ).fetchdf().to_dict('records')
    return scheme[0] if scheme else {}


def insert_location(location):
    locationID = GetAlphaNumericString(8)
    query = """
        INSERT INTO locations (id, location_type, locality, pincode, ward_number, ward_name, village, survey_village_town_city) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    db.execute(query, (
        locationID,
        location['areaType'],
        location['areaLocality'],
        location['pincode'],
        location['wardNumber'],
        location['wardName'],
        location['village'],
        location['surveyVillageTownCity']
    ))
