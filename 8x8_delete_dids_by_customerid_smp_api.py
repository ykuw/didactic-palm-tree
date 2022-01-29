import requests
import sys
import time
from config import credentials


def authentication():  # Getting the token.
	headers = {'Authorization': f'Basic {credentials}', 'Content-Type': 'application/x-www-form-urlencoded'}
	payload = {'grant_type': 'client_credentials', 'scope': 'vo'}
	sso = requests.post("https://sso.8x8.com/oauth2/v1/token", headers=headers, data=payload)
	return sso.json()["access_token"]


bearer = {'Authorization': 'Bearer ' + authentication()}  # Bearer token for the API requests.

# Getting the customer id.
customerid = input("Enter the customer id: ")
if len(customerid) < 18:
	print("Enter a valid customer id.")
	sys.exit()


def check_available_dids():
	available = requests.get(
		f"https://platform.8x8.com/vo/config/v1/customers/{customerid}/dids?filter=status==AVAILABLE", headers=bearer)
	if available.status_code == 200:
		if available.json()["pageResultSize"] != 0:
			return available.json()["content"]
		else:
			print(f"No available numbers for {customerid} that can be deleted.")
			sys.exit()
	else:
		print(f"Unable to execute the GET API request. Response code: {available.status_code}.")
		sys.exit()


dids = check_available_dids()

confirm = input(f"Do you want to delete all dids for subscription {customerid}? Enter Y or N: ")

count = 0

if confirm in ["Y", "y"]:
	for did in dids:
		deleting_dids = requests.delete(
			f"https://platform.8x8.com/vo/config/v1/customers/{customerid}/dids/{did['didId']}", headers=bearer)
		count += 1
		time.sleep(2)
	print(f"{count} dids deleted for {customerid}.")
else:
	print("Operation aborted.")
	sys.exit()
