import requests
import sys
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

log = open("dete_scim_customfields.log", "a")  # File for logging everything.
if not log.writable():
	sys.exit("Can't write to log file. Exiting the script.")


def get_users():  # Getting the user list.
	users = requests.get(f"https://platform.{url}/directory/v1/customers/{customer_id}/users/", headers=bearer)
	print(f"Getting user list for {customer_id}.")
	log.write(f"[{datetime.datetime.now()}]\tGetting user list for {customer_id}.\t{users.request.url}\n")
	if users.ok:
		return users.json()["content"]
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to get the user list. "
				  f"Response code {users.status_code}.\t{users.request.url}\n")
		sys.exit(f"Unable to get the user list. Response code {users.status_code}.")


def get_scim_user_data():  # Getting the SCIM data for each user.
	scim_customfields_url = []  # List for the SCIM data.
	count = 0  # Counting the number of users with SCIM data.
	count_no_scim = 0  # Counting the number of users without SCIM data.
	for user in get_users():
		get_user = requests.get(f"https://platform.{url}/directory/v1/customers/{customer_id}/users/{user['userId']}?"
								f"scope=expand(clientdata)'", headers=bearer)
		if get_user.ok:
			for content in get_user.json()["content"]:
				if "scimPlatform" in content:
					print(f"SCIM data for {user['userId']}.")
					scim_customfields_url.append(content["scimPlatform"]["self"])
					count += 1  # Counting the number of users with SCIM data.
					log.write(f"[{datetime.datetime.now()}]\tSCIM data for {user['userId']}.\t{get_user.request.url}\n")
				else:
					print(f"No SCIM data for {user['userId']}.")
					print(get_user.json()["content"])
					count_no_scim += 1  # Counting the number of users without SCIM data.
					log.write(
						f"[{datetime.datetime.now()}]\tNo SCIM data for {user['userId']}.\t{get_user.request.url}\n")
		else:
			print(f"Unable to get user data for {user['userId']}.")
			log.write(f"[{datetime.datetime.now()}]\tUnable to get user data for {user['userId']}. "
					  f"Response code {get_user.status_code}.\t{get_user.request.url}\n")
	print(f"SCIM data for {count} users to be deleted. {count_no_scim} users don't have SCIM data.")
	log.write(f"[{datetime.datetime.now()}]\tSCIM data for {count} users to be deleted. "
			  f"{count_no_scim} users don't have SCIM data.\n")
	return scim_customfields_url


def delete_scim_user_data():  # Deleting the SCIM data for users with SCIM data.
	count = 0
	for scim_url in get_scim_user_data():
		delete_scim_data = requests.delete(scim_url, headers=bearer)
		if delete_scim_data.ok:
			count += 1  # Counting the number of users with SCIM data deleted.
			log.write(f"[{datetime.datetime.now()}]\tDELETE {delete_scim_data.request.url} OK\n")
		else:
			print("Unable to run the DELETE request.")
			log.write(f"[{datetime.datetime.now()}]\tUnable to run the DELETE request. "
					  f"Response code {delete_scim_data.status_code}.\t{delete_scim_data.request.url}\n")
	print(f"Deleted SCIM data for {count} users.")
	log.write(f"[{datetime.datetime.now()}]\tDeleted SCIM data for {count} users.\n")


delete_scim_user_data()  # Calling the function to delete the SCIM data.

log.close()  # Closing the log file.
