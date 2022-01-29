import requests
import sys
import time
from config import credentials, url


def authentication():  # Getting the token.
	headers = {'Authorization': f'Basic {credentials}', 'Content-Type': 'application/x-www-form-urlencoded'}
	payload = {'grant_type': 'client_credentials', 'scope': 'vo'}
	sso = requests.post(f"https://sso.{url}/oauth2/v1/token", headers=headers, data=payload)
	return sso.json()["access_token"]


bearer = {'Authorization': 'Bearer ' + authentication()}  # Bearer token for the API requests.

customer = input("Enter the customer id: ").upper()  # Getting the customer id.
get_users = input("Enter the licenses to get the users from them, comma separated: ")  # Getting tel. num.

licenses = get_users.replace(" ", "").split(",")  # Removing any space character and creating a list with the input.

count = 0  # Used for counting the tel. num. removed.

file = open("output.csv", "a", encoding="utf-8")

for a_license in licenses:
	get_user = requests.get(
		f"https://platform.{url}/license/v1/customers/{customer}/licenses/{a_license}", headers=bearer)
	if get_user.ok:
		if get_user.json()["pageResultSize"] != 0:
			content = get_user.json()["content"]
			for user in content:
				if "userId" in user:
					get_name = requests.get(
						f'https://platform.{url}/vo/config/v1/customers/{customer}/users/{user["userId"]}', headers=bearer)
					if get_name.ok:
						name_content = get_name.json()["content"]
						for name in name_content:
							if "firstName" and "lastName" in name:
								print(a_license, user["userId"], name["firstName"], name["lastName"])
								file.write(f'{a_license}, {user["userId"]}, {name["firstName"]}, {name["lastName"]}\n')
							else:
								print(f'No first and last name for {user["userId"]}.')
					count += 1
				else:
					print(f"No userId for license {a_license}")
					file.write(f'{a_license}, No userId\n')
		else:
			print(f"No data for license {a_license}")
			file.write(f'{a_license}, No data\n')
		time.sleep(0.3)
	else:
		print(f"Unable to execute the API request. Response code is {get_user.status_code}.")
		sys.exit()
print(f"{count} users found.")
file.close()
