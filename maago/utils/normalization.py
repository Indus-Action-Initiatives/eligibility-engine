from datetime import datetime


def get_normalised_string_value(s):
    normalisedValue = 'unknown'

    if s != '':
        normalisedValue = s

    return normalisedValue

# possible values: true, false, unknown


def get_normalised_bool_value(s):
    normalisedValue = 'unknown'
    truthValues = ['yes']
    falseValues = ['no']
    if s in truthValues:
        normalisedValue = 'true'
    elif s in falseValues:
        normalisedValue = 'false'
    return normalisedValue


def get_normalised_float_value(s):
    value = -1
    if s != '':
        value = float(s)

    return value


def get_normalised_date_value(d, f='%d-%m-%Y'):
    value = 'NULL'
    if d != '':
        dateObject = datetime.strptime(d, f)
        value = "'" + dateObject.strftime("%Y-%m-%d") + "'"
    return value


def normalizeString(s):
    return ' '.join(s.split())
