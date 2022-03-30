import requests
import sys
import time
from config import credentials, url


if not credentials:  # Check if credentials are defined.
	sys.exit("No credentials provided. Exiting the script.")

if not url:  # Check if url is defined.
	sys.exit("No URL provided. Exiting the script.")


def authentication():  # Getting the token.
	headers = {'Authorization': f'Basic {credentials}', 'Content-Type': 'application/x-www-form-urlencoded'}
	payload = {'grant_type': 'client_credentials', 'scope': 'vo'}
	sso = requests.post(f"https://sso.{url}/oauth2/v1/token", headers=headers, data=payload)
	return sso.json()["access_token"]


bearer = {'Authorization': 'Bearer ' + authentication()}  # Bearer token for the API requests.

# Getting the customer id.
customerid = input("Enter the customer id: ")
if len(customerid) < 18:
	sys.exit("Customer id length is less than 18 characters. Exiting the script.")

# Getting the pbx id.
pbxid = input("Enter the pbx id: ")
if len(customerid) < 1:
	sys.exit("Pbx id length is less than 1 characters. Exiting the script.")

# Getting the subscription id.
subscriptionid = input("Enter the subscription id: ")
if len(customerid) < 1:
	sys.exit("Subscription id length is less than 1 characters. Exiting the script.")


def check_subscriptionid():
	subscription = requests.get(
		f"https://platform.{url}/vo/config/v1/customers/{customerid}/pbxes/{pbxid}/didbindings?filter=subscriptionId=={subscriptionid}",
		headers=bearer)
	if subscription.status_code == 200:
		if subscription.json()["pageResultSize"] != 0:
			return subscription.json()["content"]
		else:
			print(f"No PBX created for {customerid}. Creating it now based on the /customers data.")
	else:
		sys.exit(f"Unable to execute the GET API request. Response code: {subscription.status_code}.")


subscriptions = check_subscriptionid()

confirm = input(
	f"Do you want to delete all didbindings for subscription {subscriptionid}, pbx {pbxid}, customer {customerid}? "
	f"Enter Y or N: ")

count = 0

if confirm in ["Y", "y"]:
	for subscription in subscriptions:
		# print(subscription["didBindingId"])
		didbindings = requests.delete(
			f"https://platform.{url}/vo/config/v1/customers/{customerid}/pbxes/{pbxid}/didbindings/{subscription['didBindingId']}",
			headers=bearer)
		count += 1
		time.sleep(2)
	print(f"{count} didbindings deleted for subscription {subscriptionid}, pbx {pbxid}, customer {customerid}.")
else:
	sys.exit("Exiting the script.")
