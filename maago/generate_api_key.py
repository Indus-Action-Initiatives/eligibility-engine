import getopt
from app.perma_db import SingletonMySQLDB
from utils.random import generate_token

# @TODO: Get tenant id from arguments
# If tenant_id, expire the current key.
# If no key, generate a new key.

# @TODO: set expiry for key
tenant_id = ""
if (not tenant_id):
    tenant_id = "T~{}".format(generate_token())
auth_key = generate_token()

SingletonMySQLDB.add_key(tenant_id, auth_key)
print("Tenant ID:", tenant_id)
print("API Key:", auth_key)



