# checking how much tokens we have left (@TODO JP: need to make sure we get these for a given simulation)
from helm.proxy.services.remote_service import RemoteService
from helm.common.authentication import Authentication
from helm.proxy.accounts import Account

CRFM_API_KEY = "p4z0j9adj6edJOWBMnEqfPBZxAXlfOGd" # gpt4 philipp
# CRFM_API_KEY = "PncXrdFlPLSopZUeu6eqqfSwq9DKte1m" # gpt3 kanishk
# @people using crfm: add your keys here

# An example of how to use the request API.
auth = Authentication(api_key=CRFM_API_KEY)
service = RemoteService("https://crfm-models.stanford.edu")

# Access account and show my current quotas and usages (please monitor)
model = "gpt4" 
# model = "gpt3"
account: Account = service.get_account(auth)
for i, k in enumerate(account.usages[model]):
    print(f"Model: {model}, Usage {i}: {k}: {account.usages[model][k]}")