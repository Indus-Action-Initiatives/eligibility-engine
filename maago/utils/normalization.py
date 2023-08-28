from datetime import datetime
from utils import proximity_score

UNKNOWN_SCORE = 0.001
UNKNOWN_STRING = "unknown"
UNKNOWN_NUMBER = -19
UNKNOWN_DATE = datetime.strptime("30-08-1857", "%d-%m-%Y")
PROXIMITY_SCORE_KEY = "proximity_score"


def get_normalised_string_value(s):
    normalisedValue = UNKNOWN_STRING
    if s != "":
        normalisedValue = s

    return normalisedValue


# possible values: true, false, unknown
def get_normalised_bool_value(s):
    normalisedValue = UNKNOWN_STRING

    truthValues = ["yes"]
    falseValues = ["no"]
    if s in truthValues:
        normalisedValue = "true"
    elif s in falseValues:
        normalisedValue = "false"
    return normalisedValue


def get_normalised_float_value(s):
    value = UNKNOWN_NUMBER
    if s != "":
        value = float(s)

    return value


# GetDBDateString converts a date string into YYYY-mm-dd formatted string
def get_normalised_date_value(d, f="%d-%m-%Y"):
    value = "'" + str(UNKNOWN_DATE) + "'"
    if d != "":
        dateObject = datetime.strptime(d, f)
        value = "'" + dateObject.strftime("%Y-%m-%d") + "'"
    return value


def normalizeString(s):
    return " ".join(s.split())
