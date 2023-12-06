import random
import string
import secrets


# GetAlphaNumericString returns a random string of length n
def GetAlphaNumericString(n):
    randomString = ''.join(random.choice(
        string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(n))
    return randomString

def generate_token():
    return ''.join(secrets.choice(string.ascii_letters) for i in range(8))
    # return secrets.token_hex(8)