from datetime import datetime
from utils import proximity_score

def get_normalised_string_value(s):
    normalisedValue = proximity_score.UNKNOWN_STRING
    if s != '':
        normalisedValue = s

    return normalisedValue

# possible values: true, false, unknown
def get_normalised_bool_value(s):
    normalisedValue = proximity_score.UNKNOWN_STRING

    truthValues = ['yes']
    falseValues = ['no']
    if s in truthValues:
        normalisedValue = 'true'
    elif s in falseValues:
        normalisedValue = 'false'
    return normalisedValue

def get_normalised_float_value(s):
    value = proximity_score.UNKNOWN_NUMBER
    if s != '':
        value = float(s)

    return value

# GetDBDateString converts a date string into YYYY-mm-dd formatted string
def get_normalised_date_value(d, f='%d-%m-%Y'):
    value = "'" + str(proximity_score.UNKNOWN_DATE) + "'"
    if d != '':
        dateObject = datetime.strptime(d, f)
        value = "'" + dateObject.strftime("%Y-%m-%d") + "'"
    return value

def normalizeString(s):
    return ' '.join(s.split())
