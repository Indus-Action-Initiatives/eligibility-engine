import random, string

# GetAlphaNumericString returns a random string of length n
def GetAlphaNumericString(n):
    randomString = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(n))

    return randomString

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