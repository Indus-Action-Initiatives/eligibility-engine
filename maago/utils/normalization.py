from datetime import datetime


def GetNormalisedStringValue(s):
    normalisedValue = 'unknown'

    if s != '':
        normalisedValue = s

    return normalisedValue

# possible values: true, false, unknown


def GetNormalisedValue(s):
    normalisedValue = 'unknown'

    truthValues = ['yes']
    falseValues = ['no']

    if s in truthValues:
        normalisedValue = 'true'
    elif s in falseValues:
        normalisedValue = 'false'

    return normalisedValue


def GetDBFloatString(s):
    value = -1
    if s != '':
        value = float(s)

    return value


def GetDBDateString(d, f='%d-%m-%Y'):
    value = 'NULL'
    if d != '':
        dateObject = datetime.strptime(d, f)
        value = "'" + dateObject.strftime("%Y-%m-%d") + "'"
    return value


def normalizeString(s):
    return ' '.join(s.split())
