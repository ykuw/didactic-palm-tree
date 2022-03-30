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
	sys.exit("Customer id length is less than 18. Exiting the script.")


def check_available_dids():
	available = requests.get(
		f"https://platform.{url}/vo/config/v1/customers/{customerid}/dids?filter=status==AVAILABLE", headers=bearer)
	if available.status_code == 200:
		if available.json()["pageResultSize"] != 0:
			return available.json()["content"]
		else:
			sys.exit(f"No available numbers for {customerid} that can be deleted.")
	else:
		sys.exit(f"Unable to execute the GET API request. Response code: {available.status_code}.")


dids = check_available_dids()

confirm = input(f"Do you want to delete all dids for subscription {customerid}? Enter Y or N: ")

count = 0

if confirm in ["Y", "y"]:
	for did in dids:
		deleting_dids = requests.delete(
			f"https://platform.{url}/vo/config/v1/customers/{customerid}/dids/{did['didId']}", headers=bearer)
		count += 1
		time.sleep(2)
	print(f"{count} dids deleted for {customerid}.")
else:
	sys.exit("Exiting the script.")
