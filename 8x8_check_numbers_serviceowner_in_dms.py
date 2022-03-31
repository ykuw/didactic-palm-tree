import requests
import sys
import datetime
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

log = open("apis.log", "a")  # Logging all API requests.

file = open("numbers.txt", "r")  # Numbers to be checked.

if not log.writable():  # Checking if we can write the log file.
	sys.exit("Log file is not writable. Exiting the script.")

if not file.readable():  # Checking if we can read the text file.
	sys.exit("Text file is not readable. Exiting the script.")

confirmation = input(f"Checking all numbers in the text file? Enter Y or N: ")

count = 0  # Counter for all numbers found.
count_different_status = 0  # Counter for all numbers with different statuses.
count_not_found = 0  # Counter for all not found numbers.

start_time = datetime.datetime.now()  # Time it started to check all numbers.

if confirmation in ["Y", "y"]:
	for row in file.readlines():
		a_number = row.strip("\n")  # Getting one number from the text file.
		check_number = requests.get(
			f"https://platform.{url}/dms/v2/dids/?filter=phoneNumber==%2B{a_number}", headers=bearer)
		if check_number.ok:
			if check_number.json()["content"]:  # Checking if there is content in the response with data.
				for content in check_number.json()["content"]:
					if content["serviceOwner"] == "VCC":  # Checking if the number has the VCC serviceOwner.
						print(f"{a_number} has {content['serviceOwner']} service.")
						count += 1  # Counting all numbers with VCC serviceOwner.
						log.write(
							f"[{datetime.datetime.now()}]\tGET {check_number.request.url}\t{a_number} "
							f"has {content['status']} status.\n")
					else:
						print(f"{a_number} has {content['serviceOwner']} service.")  # Checking for different serviceOwner.
						count_different_status += 1  # Counting all numbers with different serviceOwner.
						log.write(
							f"[{datetime.datetime.now()}]\tGET {check_number.request.url}\t{a_number} "
							f"has {content['status']} status.\n")
			else:
				print(f"{a_number} not found in DMS.")  # Checking if the number is not found in DMS.
				count_not_found += 1  # Counting all not found numbers.
				log.write(f"[{datetime.datetime.now()}]\t{a_number} not found in DMS.")
		else:
			print(f"Unable to run the request. Response code: {check_number.status_code}.")
			log.write(f"Unable to run the request. Response code: {check_number.status_code}.\n")

	end_time = datetime.datetime.now()  # Time it ended.
	time_elapsed = end_time - start_time  # Time it took to run the script successfully for all numbers.

	print(f"{count} numbers found in DMS in {time_elapsed} with VCC service. {count_different_status} numbers with "
		  f"different service. {count_not_found} numbers not found in DMS.")
	log.write(f"[{datetime.datetime.now()}]\t{count} numbers found in {time_elapsed}. {count_not_found} resulted in "
			  f"not found in DMS.\n")
else:
	log.write(f"[{datetime.datetime.now()}]\tExiting the script.\n")
	sys.exit("Exiting the script.")

file.close()
log.close()
