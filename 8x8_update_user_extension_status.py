import requests
import sys
import datetime
from config import credentials, customer_id, url, pbx_id


if not credentials:  # Check if credentials are defined.
	sys.exit("No credentials provided. Exiting the script.")

if not url:  # Check if url is defined.
	sys.exit("No URL provided. Exiting the script.")

if not customer_id:  # Check if customer_id is defined.
	sys.exit("No customer_id provided. Exiting the script.")

if not pbx_id:  # Check if pbx_id is defined.
	sys.exit("No pbx_id provided. Exiting the script.")


def authentication():  # Getting the token.
	headers = {'Authorization': f'Basic {credentials}', 'Content-Type': 'application/x-www-form-urlencoded'}
	payload = {'grant_type': 'client_credentials', 'scope': 'vo'}
	sso = requests.post(f"https://sso.{url}/oauth2/v1/token", headers=headers, data=payload)
	return sso.json()["access_token"]


bearer = {'Authorization': 'Bearer ' + authentication()}  # Bearer token for the API requests.

log = open("apis.log", "a")  # Logging all API requests.

file = open("extensions.txt", "r")  # User extensions.

if not log.writable():  # Checking if we can write the log file.
	sys.exit("Can't write to the log file. Exiting the script.")

if not file.readable():  # Checking if we can read the text file.
	sys.exit("Can't read the text file. Exiting the script.")

confirmation = input(f"Do you want to change the status for all users in the text file to false for {customer_id}? "
					 f"Enter Y or N: ")

count = 0  # Counter for all user extensions updated.

start_time = datetime.datetime.now()  # Time it started to update the user extensions.

if confirmation in ["Y", "y"]:
	for row in file.readlines():
		a_extension = row.strip("\n")
		payload = {
			"command": "updateExtension",
			"arguments": {
				"number": f"{a_extension}",
				"dnd": "false"
			}
		}
		change_status = requests.post(
			f"https://platform.8x8.com/vo/config/v1/customers/{customer_id}/pbxes/{pbx_id}/_tclcommand", headers=bearer,
			json=payload)
		if change_status.ok:
			print(f"Status changed for extension {a_extension}, customer {customer_id}.")
			count += 1
			log.write(
				f"[{datetime.datetime.now()}]\tPOST {change_status.request.url}\tStatus changed for extension"
				f" {a_extension}, customer {customer_id}.\n")
		else:
			print(f"{a_extension} not found for {customer_id}.")
			log.write(f"{a_extension} not found for {customer_id}.\n")
	end_time = datetime.datetime.now()  # Time it ended.
	time_elapsed = end_time - start_time  # Time it took to run the script successfully for all licenses.
	print(f"{count} extensions updated in {time_elapsed}.")
	log.write(f"[{datetime.datetime.now()}]\t{count} extensions updated in {time_elapsed}.\n")
else:
	log.write(f"[{datetime.datetime.now()}]\tScript aborted.\n")
	sys.exit("Exiting the script.")

file.close()
log.close()
