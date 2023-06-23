import random
import string


# GetAlphaNumericString returns a random string of length n
def GetAlphaNumericString(n):
    randomString = ''.join(random.choice(
        string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(n))

    return randomString