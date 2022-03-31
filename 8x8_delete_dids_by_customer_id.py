import requests
import sys
import time
import datetime
from config import credentials, url, customer_id


if not credentials:  # Check if credentials are defined.
	sys.exit("No credentials provided. Exiting the script.")

if not url:  # Check if url is defined.
	sys.exit("No URL provided. Exiting the script.")

if not customer_id:  # Check if customer_id is defined.
	sys.exit("No customer_id provided. Exiting the script.")


def authentication():  # Getting the token.
	headers = {'Authorization': f'Basic {credentials}', 'Content-Type': 'application/x-www-form-urlencoded'}
	payload = {'grant_type': 'client_credentials', 'scope': 'vo'}
	sso = requests.post(f"https://sso.{url}/oauth2/v1/token", headers=headers, data=payload)
	return sso.json()["access_token"]


bearer = {'Authorization': 'Bearer ' + authentication()}  # Bearer token for the API requests.

log = open("apis.log", "a")  # Logging all API requests.

if not log.writable():  # Checking if we can write the log file.
	sys.exit("The log file is not writable. Exiting the script.")


def check_available_dids():
	available = requests.get(
		f"https://platform.{url}/vo/config/v1/customers/{customer_id}/dids?filter=status==AVAILABLE", headers=bearer)
	if available.ok:
		if available.json()["pageResultSize"] != 0:
			return available.json()["content"]
		else:
			log.write(f"[{datetime.datetime.now()}]\tNo available numbers found for customer {customer_id}.\n")
			sys.exit(f"No available numbers for {customer_id} that can be deleted.")
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to execute the request. Response code: {available.status_code}\n")
		sys.exit(f"Unable to execute the request. Response code: {available.status_code}.")


dids = check_available_dids()  # Getting the available DIDs.

confirm = input(f"Do you want to delete all dids for subscription {customer_id}? Enter Y or N: ")

count = 0  # Counting the number of DIDs that will be deleted.

if confirm in ["Y", "y"]:
	for did in dids:
		deleting_dids = requests.delete(
			f"https://platform.{url}/vo/config/v1/customers/{customer_id}/dids/{did['didId']}", headers=bearer)

		count += 1  # Counting the number of DIDs that have been deleted.
		log.write(f"[{datetime.datetime.now()}]\t{deleting_dids.request.url}")
		time.sleep(2)  # Sleep for 2 seconds.

	print(f"{count} dids deleted for {customer_id}.")
	log.write(f"[{datetime.datetime.now()}]\t{count} dids deleted for {customer_id}.\n")
else:
	log.write(f"[{datetime.datetime.now()}]\tExiting the script.\n")
	sys.exit("Exiting the script.")

log.close()  # Closing the log file.
