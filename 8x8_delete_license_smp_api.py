import requests
import sys
import datetime
from config import credentials, url, customer_id


if not credentials:  # Check if credentials are defined.
	sys.exit("No credentials provided. Exiting the script.")

if not url:  # Check if url is defined.
	sys.exit("No URL provided. Exiting the script.")

if not customer_id:  # Check if customer_id is defined.
	sys.exit("No customer id provided. Exiting the script.")


def authentication():  # Getting the token.
	headers = {'Authorization': f'Basic {credentials}', 'Content-Type': 'application/x-www-form-urlencoded'}
	payload = {'grant_type': 'client_credentials', 'scope': 'vo'}
	sso = requests.post(f"https://sso.{url}/oauth2/v1/token", headers=headers, data=payload)
	return sso.json()["access_token"]


bearer = {'Authorization': 'Bearer ' + authentication()}  # Bearer token for the API requests.

log = open("apis.log", "a")  # Logging all API requests.

file = open("licenses.txt", "r")  # Licenses to be deleted.

if not log.writable():  # Checking if we can write the log file.
	sys.exit("Cannot write to the log file. Exiting the script.")

if not file.readable():  # Checking if we can read the text file.
	sys.exit("Cannot read the text file. Exiting the script.")

confirmation = input(f"Do you want to delete all licenses from the text file for {customer_id}? Enter Y or N: ")

count = 0  # Counter for all licenses deleted.

start_time = datetime.datetime.now()  # Time it started to delete licenses.

if confirmation in ["Y", "y"]:
	for row in file.readlines():
		a_license = row.strip("\n")
		delete_license = requests.delete(
			f"https://platform.{url}/license/v1/customers/{customer_id}/licenses/{a_license}", headers=bearer)
		if delete_license.ok:
			print(f"{a_license} deleted for {customer_id}.")
			count += 1  # Counting the deleted licenses.
			log.write(
				f"[{datetime.datetime.now()}]\tDELETE {delete_license.request.url}\t{a_license} deleted for {customer_id}.\n")
		else:
			print(f"{a_license} not found for {customer_id}.")
			log.write(f"[{datetime.datetime.now()}]\t{a_license} not found for {customer_id}.\n")

	end_time = datetime.datetime.now()  # Time it ended.
	time_elapsed = end_time - start_time  # Time it took to run the script successfully for all licenses.

	print(f"{count} total licenses deleted in {time_elapsed}.")
	log.write(f"[{datetime.datetime.now()}]\t{count} total licenses deleted in {time_elapsed}.\n")
else:
	log.write(f"[{datetime.datetime.now()}]\tExiting the script.\n")
	sys.exit("Exiting the script.")

file.close()  # Closing the text file.
log.close()  # Closing the log file.
