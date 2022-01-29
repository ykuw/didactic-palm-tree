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

tenant = input("Enter the tenant name: ")  # Getting tenant name.
site = input("Enter the site: ").upper()  # Getting the site for the tenant. Making the input uppercase.
cluster = input("Enter the cluster: ").upper()  # Getting the cluster for the tenant. Making the input uppercase.
get_numbers = input("Enter the telephone numbers to be deleted, comma separated: ")  # Getting tel. num.

numbers = get_numbers.replace(" ", "").split(",")  # Removing any space character and creating a list with the input.

# If no number is entered, exiting the script.
if len(numbers) > 0:
	confirmation = input(f"Do you want to remove all telephone numbers pasted for {tenant}? Enter Y or N: ")
else:
	print("No numbers provided, exiting the script.")
	sys.exit()

count = 0  # Used for counting the tel. num. removed.

if confirmation in ["Y", "y"]:
	for number in numbers:
		xml = f'<request><user id="pma" agent="Account Manager"></user><phone clidblk="enabled" calling-name="8x8, ' \
			  f'Inc." site="{site}" cluster="{cluster}"></phone></request>'
		delete_number = requests.post(
			f"https://vcc-provapi-prod.8x8.com/tenant/{tenant}/phone/delete/{number}", headers=bearer, data=xml)
		if delete_number.status_code == 200:
			print(f"Successfully removed {number} from {tenant}!")
			count += 1
			time.sleep(5)
		else:
			print(f"Unable to execute the API request. Response code is {delete_number.status_code}.")
			sys.exit()
	print(f"{count} telephone numbers deleted for {tenant} from VCC CM.")
else:
	print("Operation aborted.")
	sys.exit()
