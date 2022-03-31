import requests
import sys
import time
from config import credentials, url, customer_id, pbx_id, subscription_id


if not credentials:  # Check if credentials are defined.
	sys.exit("No credentials provided. Exiting the script.")

if not url:  # Check if url is defined.
	sys.exit("No URL provided. Exiting the script.")

if not customer_id:  # Check if customer_id is defined.
	sys.exit("No customer_id provided. Exiting the script.")

if not pbx_id:  # Check if pbx_id is defined.
	sys.exit("No pbx_id provided. Exiting the script.")

if not subscription_id:  # Check if subscription_id is defined.
	sys.exit("No subscription_id provided. Exiting the script.")


def authentication():  # Getting the token.
	headers = {'Authorization': f'Basic {credentials}', 'Content-Type': 'application/x-www-form-urlencoded'}
	payload = {'grant_type': 'client_credentials', 'scope': 'vo'}
	sso = requests.post(f"https://sso.{url}/oauth2/v1/token", headers=headers, data=payload)
	return sso.json()["access_token"]


bearer = {'Authorization': 'Bearer ' + authentication()}  # Bearer token for the API requests.

log = open("apis.log", "a")  # Logging all API requests.

if not log.writable():  # Checking if we can write the log file.
	sys.exit("The log file is not writable. Exiting the script.")


def check_subscription_id():
	subscription = requests.get(
		f"https://platform.{url}/vo/config/v1/customers/{customer_id}/pbxes/{pbx_id}/didbindings"
		f"?filter=subscriptionId=={subscription_id}",
		headers=bearer)
	if subscription.status_code == 200:
		if subscription.json()["pageResultSize"] != 0:
			return subscription.json()["content"]
		else:
			print(f"No PBX created for {customer_id}. Creating it now based on the /customers data.")
			log.write("No PBX created for {customer_id}. Creating it now based on the /customers data.\n")
	else:
		log.write(f"Error: {subscription.status_code} - {subscription.request.url}\n")
		sys.exit(f"Unable to execute the GET API request. Response code: {subscription.status_code}.")


subscriptions = check_subscription_id()

confirm = input(
	f"Do you want to delete all didbindings for subscription {subscription_id}, pbx {pbx_id}, customer {customer_id}? "
	f"Enter Y or N: ")

count = 0

if confirm in ["Y", "y"]:
	for subscription in subscriptions:
		didbindings = requests.delete(
			f"https://platform.{url}/vo/config/v1/customers/{customer_id}/pbxes/{pbx_id}/didbindings/{subscription['didBindingId']}",
			headers=bearer)
		log.write(f"{didbindings.status_code} - {didbindings.request.url}\n")
		count += 1
		time.sleep(2)
	print(f"{count} didbindings deleted for subscription {subscription_id}, pbx {pbx_id}, customer {customer_id}.")
	log.write(f"{count} didbindings deleted for subscription {subscription_id}, pbx {pbx_id}, customer {customer_id}.\n")
else:
	log.write(f"Exiting the script.\n")
	sys.exit("Exiting the script.")
