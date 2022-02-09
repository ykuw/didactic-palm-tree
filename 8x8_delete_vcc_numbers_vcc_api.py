import datetime
import requests
from requests import adapters
import sys
import ssl
from config import credentials, url, site, cluster, customer_id


def authentication():  # Getting the token.
	headers = {'Authorization': f'Basic {credentials}', 'Content-Type': 'application/x-www-form-urlencoded'}
	payload = {'grant_type': 'client_credentials', 'scope': 'vo'}
	sso = requests.post(f"https://sso.{url}/oauth2/v1/token", headers=headers, data=payload)
	return sso.json()["access_token"]


class TLSAdapter(adapters.HTTPAdapter):  # This solves a SSL issue
	# That issue is 'ssl.SSLError: [SSL: WRONG_SIGNATURE_TYPE] wrong signature type (_ssl.c:997)'
	def init_poolmanager(self, *args, **kwargs):
		ctx = ssl.create_default_context()
		ctx.set_ciphers('DEFAULT@SECLEVEL=1')
		kwargs['ssl_context'] = ctx
		return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)


session = requests.session()
session.mount('https://', TLSAdapter())

bearer = {'Authorization': 'Bearer ' + authentication(), 'Content-Type': 'application/xml'}

log = open("apis.log", "a")  # Logging all API requests.

file = open("numbers.txt", "r")  # Licenses to be removed.

if not log.writable():  # Checking if we can write the log file.
	print("Cannot write the log file.")
	sys.exit()

if not file.readable():  # Checking if we can read the text file.
	print("Cannot read the text file.")
	sys.exit()

confirmation = input(f"Do you want to remove all numbers the text file for {customer_id}? Enter Y or N: ")

count = 0  # Used for counting the tel. num. removed.

if confirmation in ["Y", "y"]:
	for row in file.readlines():
		a_number = row.strip("\n")
		xml = f'<request><user id="pma" agent="Account Manager"></user><phone clidblk="enabled" ' \
			  f'calling-name="8x8, Inc." site="{site.upper()}" cluster="{cluster.upper()}"></phone></request>'
		delete_number = session.post(f"https://vcc-provapi-prod.{url}/tenant/{customer_id}/phone/delete/{a_number}",
									 headers=bearer, data=xml)
		if delete_number.ok:
			print(f"Successfully removed {a_number} from {customer_id}!")
			log.write(f"[{datetime.datetime.now()}]\tSuccessfully removed {a_number} from "
					  f"{customer_id}!\t{delete_number.request.url}\t{delete_number.status_code}\t{delete_number.request.body}\n")
			count += 1
		else:
			print(f"Unable to execute the API request. Response code is {delete_number.status_code}.")
			log.write(f"[{datetime.datetime.now()}]\tUnable to execute the API request. Response code "
					  f"is {delete_number.status_code}\t{delete_number.request.url}\t{delete_number.request.body}\n")
			sys.exit()
	print(f"{count} telephone numbers removed for {customer_id} from VCC CM.")
	log.write(f"[{datetime.datetime.now()}]\t{count} telephone numbers deleted for {customer_id} from VCC CM.\n")
else:
	print("Operation aborted.")
	log.write(f"[{datetime.datetime.now()}]\tOperation aborted.\n")
	sys.exit()
