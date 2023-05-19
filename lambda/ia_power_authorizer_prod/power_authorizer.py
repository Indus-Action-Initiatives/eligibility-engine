import json
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode

import re
import time

# global start up params
time_offset = 240
user_regex = r".+@\bpower\b|.+@\bpoweruat\b"
issuer_url = "https://cognito-idp.ap-south-1.amazonaws.com/ap-south-1_DU27AHJvZ"
app_client_id = "1d6rgvitjsfoonlkbm07uivgmg"
keys_url = "{}/.well-known/jwks.json".format(issuer_url)

# download the public keys
with urllib.request.urlopen(keys_url) as f:
    response = f.read()
keys = json.loads(response.decode("utf-8"))["keys"]


def generate_policy(principal_id, effect, method_arn):
    """ return a valid AWS policy response """
    auth_response = {"principalId": principal_id}
    if effect and method_arn:
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "FirstStatement",
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": method_arn,
                }
            ],
        }
        auth_response["policyDocument"] = policy_document
    return auth_response


def lambda_handler(event, context):
    token = event["authorizationToken"].replace("Bearer ", "")
    method_arn = event["methodArn"]

    headers = jwt.get_unverified_headers(token)
    kid = headers["kid"]

    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]["kid"]:
            key_index = i
            break
    if key_index == -1:
        print("Public key not found in jwks.json")
        return False
    # construct the public key
    public_key = jwk.construct(keys[key_index])

    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit(".", 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))

    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print("Signature verification failed")
        return False
    print("Signature successfully verified")

    # use the unverified claims
    claims = jwt.get_unverified_claims(token)

    if time.time() > time_offset + claims["exp"]:
        print("Token timeout")
        return generate_policy(claims["cognito:username"], "Deny", method_arn)
    if not re.search(user_regex, claims["cognito:username"]):
        print("Incorrect user group")
        return generate_policy(claims["cognito:username"], "Deny", method_arn)
    if claims["iss"] != issuer_url:
        print("Token not issued from correct source")
        return generate_policy(claims["cognito:username"], "Deny", method_arn)
    if claims["aud"] != app_client_id:
        print("Token was not issued for this audience")
        return generate_policy(claims["cognito:username"], "Deny", method_arn)
    # generate policy
    policy = generate_policy(claims["cognito:username"], "Allow", method_arn)
    return policy