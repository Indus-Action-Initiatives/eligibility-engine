import random, string
from datetime import datetime

# GetAlphaNumericString returns a random string of length n
def GetAlphaNumericString(n):
    randomString = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(n))

    return randomString

# GetDBDateString converts a date string into YYYY-mm-dd formatted string
def GetDBDateString(d, f='%d-%m-%Y'):
    value = 'NULL'
    if d != '':
        dateObject = datetime.strptime(d, f)
        value = "'" + dateObject.strftime("%Y-%m-%d") + "'"
    
    return value

def GetDBFloatString(s):
    value = -1
    if s != '':
        value = float(s)

    return value

# possible values: true, false, unkown
def GetNormalisedValue(s):
    normalisedValue = 'unknown'

    truthValues = ['yes']
    falseValues = ['no']

    if s in truthValues:
        normalisedValue = 'true'
    elif s in falseValues:
        normalisedValue = 'false'

    return normalisedValue