import requests
import sys
import time
import datetime
from config import credentials, url, customer_id, user_first_name, user_last_name, user_email

if not credentials:  # Check if credentials are defined.
	sys.exit("No credentials provided. Exiting the script.")

if not url:  # Check if url is defined.
	sys.exit("No URL provided. Exiting the script.")

if not customer_id:  # Check if customer_id is defined.
	sys.exit("No customer_id provided. Exiting the script.")

if not user_first_name:  # Check if user_first_name is defined.
	sys.exit("No user_first_name provided. Exiting the script.")

if not user_last_name:  # Check if user_last_name is defined.
	sys.exit("No user_last_name provided. Exiting the script.")


def authentication():  # Getting the token.
	headers = {'Authorization': f'Basic {credentials}', 'Content-Type': 'application/x-www-form-urlencoded'}
	payload = {'grant_type': 'client_credentials', 'scope': 'vo'}
	sso = requests.post(f"https://sso.{url}/oauth2/v1/token", headers = headers, data = payload)
	return sso.json()["access_token"]


bearer = {
	'Authorization': 'Bearer ' + authentication(),
	'Content-Type': 'application/json'
}  # Bearer token for the API requests.

log = open("apis.log", "a")  # Logging all API requests.

if not log.writable():  # Check if log file is writable.
	sys.exit("The log file is not writable. Exiting the script.")


# 1 - Customer Validation
# Checking if the customer exists in '/customers' in SMP.
def check_customers():
	customers = requests.get(f"https://platform.{url}/vo/config/v1/customers/{customer_id}", headers = bearer)
	time.sleep(1)  # Sleep for 1 second.
	if customers.ok:
		if customers.json()["pageResultSize"] != 0:
			log.write(f"[{datetime.datetime.now()}]\t{customers.json()['content']}\n")
			return customers.json()["content"]
		else:
			log.write(f"[{datetime.datetime.now()}]\tNo results for {customer_id}. Have you typed the correct customer "
			          f"id? If not, possibly the workflow needs to be restarted.\n")
			sys.exit(f"No results for {customer_id}. Have you typed the correct customer id? If not, possibly the "
			         f"workflow needs to be restarted.")
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to execute the GET API request. "
		          f"Response code: {customers.status_code}. Step one. - {customers.request.url}\n")
		sys.exit(f"Unable to execute the GET API request. Response code: {customers.status_code}. Step one. - "
		         f"{customers.request.url}")


customer = check_customers()  # Calling the function to check if the customer exists in '/customers' in SMP.


# 2 - PBX Validation
def pbx_payload():
	for info in customer:
		if info["contactAddress"]["country"] == "GB":
			region = "GBR"
		elif (info["contactAddress"]["country"] == "US") or (info["contactAddress"]["country"] == "CA"):
			region = "USA"
		elif info["contactAddress"]["country"] == "AU":
			region = "AUS"
		elif info["contactAddress"]["country"] == "CN":
			region = "CHN"
		else:
			region = input("The country is nor GB or US, enter it: ")
		name = ''.join(e for e in info["name"].lower() if e.isalnum())
		# Lowering the chars for the name and removing any special char.
		timezone_id = info["timeZoneId"]
		dialplan_name = info["VO"]["details"]["defaultDialPlan"]
		dialplan_rule_set_name = info["VO"]["details"]["defaultDialPlanRuleSet"]
		locale = info["locale"]
		free_form = info["contactAddress"]["freeForm"]
		country = info["contactAddress"]["country"]
		payload = {
			"region": f"{region}",
			"status": "ACTIVE",
			"name": f"{name[:15]}",  # Limiting the name to 15 chars.
			"customerId": f"{customer_id}",
			"timeZoneId": f"{timezone_id}",
			"dialPlanName": f"{dialplan_name}",
			"dialPlanRuleSetName": f"{dialplan_rule_set_name}",
			"details": {
				"classType": "SMB",
				"type": "VIRTUAL_OFFICE",
				"maxSwitchBoardConnections": 0,
				"emergencyAddress": {
					"freeForm": f"{free_form}",
					"country": f"{country}",
					"validationSource": "USER",
					"verified": "true"
				},
				"extensionLength": "4"
			},
			"locale": f"{locale}"
		}
		return payload


def create_pbx():
	print(f"Creating a PBX for {customer_id} & taking a 3 min break for it to be processed.")
	pbx_data = requests.post(f"https://platform.{url}/vo/config/v1/customers/{customer_id}/pbxes", headers = bearer,
	                         json = pbx_payload())
	if pbx_data.ok:
		print("Done. Step two completed!")
		log.write(f"[{datetime.datetime.now()}]\tDone. Step two "
		          f"completed!\t{pbx_data.request.url}\t{pbx_data.request.body}\t{pbx_data.request.headers}\n")
		time.sleep(180)  # Sleep for 3 minutes.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to execute the POST API request. Response "
		          f"code: {pbx_data.status_code}. Step two. - "
		          f"{pbx_data.request.url}\t{pbx_data.request.body}\t{pbx_data.request.headers}\n")
		sys.exit(f"Unable to create the PBX. Status code returned is {pbx_data.status_code}. Step two. - "
		         f"{pbx_data.request.url}\t{pbx_data.request.body}\t{pbx_data.request.headers}")


def check_pbxes():
	pbxes = requests.get(f"https://platform.{url}/vo/config/v1/customers/{customer_id}/pbxes", headers = bearer)
	time.sleep(1)  # Sleeping for 1 sec.
	if pbxes.ok:
		if pbxes.json()["pageResultSize"] != 0:
			log.write(f"{pbxes.json()['content']}\n")
			return pbxes.json()["content"]
		else:
			print(f"No PBX created for {customer_id}. Creating it now based on the '/customers' data.")
			log.write(f"[{datetime.datetime.now()}]\tNo PBX created for {customer_id}. Creating it "
			          f"now based on the '/customers' data.\n")
			create_pbx()  # Calling the function to create the PBX.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to execute the GET API request."
		          f" Response code: {pbxes.status_code}. Step two. - "
		          f"{pbxes.request.url}\t{pbxes.request.body}\t{pbxes.request.headers}\n")
		sys.exit(f"Unable to execute the GET API request. Response code: {pbxes.status_code}. Step two. - "
		         f"{pbxes.request.url}")


check_pbxes()  # Calling the function to check the PBX.


def get_pbx():
	for pbx in check_pbxes():
		if pbx["pbxId"] != '':
			log.write(f"[{datetime.datetime.now()}]\tPBX ID: {pbx['pbxId']}\n")
			return pbx["pbxId"]
		break


# 3 - Site Validation
def branch_payload():
	for info in customer:
		name = ''.join(e for e in info["name"].lower() if e.isalnum())
		# Lowering the chars for the name and removing any special char.
		timezone_id = info["timeZoneId"]
		dialplan_name = info["VO"]["details"]["defaultDialPlan"]
		dialplan_rule_set_name = info["VO"]["details"]["defaultDialPlanRuleSet"]
		locale = info["locale"]
		free_form = info["contactAddress"]["freeForm"]
		country = info["contactAddress"]["country"]
		payload = {
			"status": "ACTIVE",
			"name": f"{name}",
			"customerId": f"{customer_id}",
			"pbxId": f"{get_pbx()}",
			"dialPlanName": f"{dialplan_name}",
			"dialPlanRuleSetName": f"{dialplan_rule_set_name}",
			"timeZoneId": f"{timezone_id}",
			"branchCodeLength": 0,
			"isDefault": "true",
			"details": {
				"mainNumberAsCallerId": "false",
				"emergencyAddress": {
					"freeForm": f"{free_form}",
					"country": f"{country}",
					"validationSource": "USER",
					"verified": "true"
				},
				"extensionLength": 4
			},
			"locale": f"{locale}"
		}
		return payload


def create_branch():
	# Creating the branch.
	branch_data = requests.post(
		f"https://platform.{url}/vo/config/v1/customers/{customer_id}/pbxes/{get_pbx()}/branches",
		headers = bearer, json = branch_payload())
	if branch_data.ok:
		print(f"Created a branch for {customer_id}. Step three completed! Taking a 2 sec break.")
		log.write(f"[{datetime.datetime.now()}]\tCreated a branch for {customer_id}. Step three "
		          f"completed! Taking a 2 sec break.\n")
		time.sleep(2)  # Sleep for 2 sec.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to create a branch. Response "
		          f"code {branch_data.status_code}. Step three. - "
		          f"{branch_data.request.url}\t{branch_data.request.body}\t{branch_data.request.headers}\n")
		sys.exit(f"Unable to create a branch. Response code {branch_data.status_code}. Step three. - "
		         f"{branch_data.request.url}, {branch_data.request.body}, {branch_data.request.headers}")


def check_branch():
	branch = requests.get(f"https://platform.{url}/vo/config/v1/customers/{customer_id}/branches", headers = bearer)
	time.sleep(1)  # Sleeping for 1 sec.
	if branch.ok:
		if branch.json()["pageResultSize"] != 0:
			print("Checking if there is branch data.")
			log.write("[{datetime.datetime.now()}]\tChecking if there is branch data.\n")
		else:
			print(f"No branch created for {customer_id}. Creating it now based on the '/customers' data.")
			log.write(f"[{datetime.datetime.now()}]\tNo branch created for {customer_id}. Creating it now based "
			          f"on the '/customers' data.\n")
			create_branch()  # Calling the function to create the branch.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to execute the GET API request. Response "
		          f"code: {branch.status_code}. Step three. - "
		          f"{branch.request.url}\t{branch.request.body}\t{branch.request.headers}\n")
		sys.exit(f"Unable to execute the GET API request. Response code: {branch.status_code}. Step three. - "
		         f"{branch.request.url}")


check_branch()  # Calling the function to check the branch.


# 4 - Call-Park Validation
def create_call_park():
	# Creating the Call-Park data.
	call_park_data = requests.post(
		f"https://platform.{url}/vo/config/v1/customers/{customer_id}/pbxes/{get_pbx()}/callparks/_default",
		headers = bearer)
	if call_park_data.ok:
		print(f"Created the Call-Park data for {customer_id}. Step four completed! Taking a 2 sec break.")
		log.write(f"Created the Call-Park data for {customer_id}. Step four completed! Taking a 2 sec break.\n")
		time.sleep(2)  # Sleep for 2 sec.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to create the Call-Park data. Response "
		          f"code {call_park_data.status_code}. Step four. - "
		          f"{call_park_data.request.url}\t{call_park_data.request.body}\t{call_park_data.request.headers}\n")
		sys.exit(f"Unable to execute the POST API request. Response code {call_park_data.status_code}. Step four. - "
		         f"{call_park_data.request.url}, {call_park_data.request.body}, {call_park_data.request.headers}")


def check_call_park():
	call_park = requests.get(
		f"https://platform.{url}/vo/config/v1/customers/{customer_id}/pbxes/{get_pbx()}/callparks/",
		headers = bearer)
	time.sleep(1)  # Sleep for 1 sec.
	if call_park.ok:
		if call_park.json()["pageResultSize"] != 0:
			print("Checking if there is call park data.")
			log.write(f"[{datetime.datetime.now()}]\tChecking if there is call park data.\n")
		else:
			print(f"There is no call park data for {customer_id}. Creating it now on PBX {get_pbx()}.")
			log.write(f"[{datetime.datetime.now()}]\tThere is no call park data for {customer_id}. Creating "
			          f"it now on PBX {get_pbx()}.\n")
			create_call_park()  # Calling the function to create the call park data.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to execute the GET API request. Response "
		          f"code: {call_park.status_code}. Step four. - "
		          f"{call_park.request.url}\t{call_park.request.body}\t{call_park.request.headers}\n")
		sys.exit(f"Unable to execute the GET API request. Response code: {call_park.status_code}. Step four. -"
		         f"{call_park.request.url}")


check_call_park()  # Calling the function to check the call park data.


# 5 - User DB Validation. Part one.
def user_payload():
	for info in customer:
		timezone_id = info["timeZoneId"]
		payload = {
			"customerId": f"{customer_id}",
			"loginId": f"{user_email}",
			"firstName": f"{user_first_name}",
			"lastName": f"{user_last_name}",
			"primaryEmail": f"{user_email}",
			"tags": "protected",
			"locale": "en-US",
			"timeZoneId": f"{timezone_id}"
		}
		return payload


def create_user_db():
	# Creating the main admin.
	user_db = requests.post(f"https://platform.{url}/vo/config/v1/customers/{customer_id}/users", headers = bearer,
	                        json = user_payload())
	if user_db.ok:
		print(f"Created the main admin for {customer_id}. Step five, part one, completed! Taking a 2 sec break.")
		log.write(f"[{datetime.datetime.now()}]\tCreated the main admin for {customer_id}. Step five, "
		          f"part one, completed! Taking a 2 sec break.\n")
		time.sleep(2)  # Sleep for 2 sec.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to create the main admin. Response code {user_db.status_code}. "
		          f"Step five, part one. - "
		          f"{user_db.request.url}\t{user_db.request.body}\t{user_db.request.headers}\n")
		sys.exit(f"Unable to execute the POST API request. Make sure the user is not in '/directory'. "
		         f"Response code {user_db.status_code}. Step five, part one. - "
		         f"{user_db.request.url}, {user_db.request.body}, {user_db.request.headers}")


def check_user_db():
	user_db = requests.get(f"https://platform.{url}/vo/config/v1/customers/{customer_id}/users/", headers = bearer)
	time.sleep(1)  # Sleep for 1 sec.
	if user_db.ok:
		if user_db.json()["pageResultSize"] != 0:
			log.write(f"[{datetime.datetime.now()}]\tChecking if there is user data. {user_db.json()['content']}\n")
			return user_db.json()["content"]
		else:
			print(f"There is no user data for {customer_id}. Creating a main admin.")
			log.write(f"[{datetime.datetime.now()}]\tThere is no user data for {customer_id}. Creating a main admin.\n")
			create_user_db()  # Calling the function to create the user that will be the main admin.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to execute the GET API request. Response "
		          f"code: {user_db.status_code}. Step five, part one. - "
		          f"{user_db.request.url}\t{user_db.request.body}\t{user_db.request.headers}\n")
		sys.exit(f"Unable to execute the GET API request. Response code: {user_db.status_code}. Step five, part one. -"
		         f"{user_db.request.url}")


check_user_db()  # Calling the function to check the user data.


def get_user():
	for user in check_user_db():
		if user["userId"] != '':
			log.write(f"[{datetime.datetime.now()}]\tUser ID: {user['userId']}\n")
			return user["userId"]
		break


# 5 - User DB Validation. Part two.
def role_payload():
	payload = {
		"resources": [f"{customer_id}"],
		"roleId": "Wz8uYQNuokCMIUpr8Xg8lg",
		"resourceClassId": "87wl3cVLfkmT3vLtjxIbmA",
		"status": "ACTIVE",
		"accessorType": "USER"
	}
	return payload


def create_admin_role():
	# Creating the main admin.
	admin_role = requests.post(
		f"https://platform.{url}/rolemgmt/v1/customers/{customer_id}/accessors/{get_user()}/roles", headers = bearer,
		json = role_payload())
	if admin_role.ok:
		print(f"Created the admin role for user {get_user()}. Step five, part two, completed! Taking a 2 sec break.")
		log.write(f"[{datetime.datetime.now()}]\tCreated the admin role for user {get_user()}. Step five, "
		          f"part two, completed! Taking a 2 sec break.\n")
		time.sleep(2)  # Sleep for 2 sec.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to create the admin role. Response "
		          f"code {admin_role.status_code}. Step five, part two. - "
		          f"{admin_role.request.url}\t{admin_role.request.body}\t{admin_role.request.headers}\n")
		sys.exit(
			f"Unable to execute the POST API request. Response code {admin_role.status_code}. Step five, part two. -"
			f"{admin_role.request.url}, {admin_role.request.body}, {admin_role.request.headers}")


def check_user_role():
	user_role = requests.get(
		f"https://platform.{url}/rolemgmt/v1/customers/{customer_id}/accessors/{get_user()}/roles", headers = bearer)
	time.sleep(1)  # Sleep for 1 sec.
	if user_role.ok:
		if user_role.json()["pageResultSize"] != 0:
			for role in user_role.json()["content"]:
				if role["roleName"] == "CUSTOMER_ADMIN":
					print(f"There is an admin role for user {get_user()}.")
					log.write(f"[{datetime.datetime.now()}]\tThere is an admin role for user {get_user()}.\n")
				else:
					print("The existent user is not an admin. Making it an admin now.")
					log.write(
						f"[{datetime.datetime.now()}]\tThe existent user is not an admin. Making it an admin now.\n")
					create_admin_role()
		else:
			print(f"There is no role for the user. Creating one now.")
			log.write(f"[{datetime.datetime.now()}]\tThere is no role for the user. Creating one now.\n")
			create_admin_role()  # Calling the function to create the admin role.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to execute the GET API request. Response "
		          f"code: {user_role.status_code}. Step five, part two. -"
		          f"{user_role.request.url}\t{user_role.request.body}\t{user_role.request.headers}\n")
		sys.exit(f"Unable to execute the GET API request. Step five, part two.")


check_user_role()  # Calling the function to check if the user has a role.


# 5 - User DB Validation. Part three.
def admin_protected_tag_payload():
	payload = {
		"name": "protected"
	}
	return payload


def create_admin_protected_tag():
	# Creating the main admin.
	admin_protected_tag = requests.post(
		f"https://platform.{url}/rolemgmt/v1/customers/{customer_id}/accessors/{get_user()}/roles", headers = bearer,
		json = admin_protected_tag_payload())
	if admin_protected_tag.ok:
		print(
			f"Created the protected tag for user {get_user()}. Step five, part three, completed! Taking a 2 sec break.")
		log.write(f"[{datetime.datetime.now()}]\tCreated the admin role for user {get_user()}. Step five, "
		          f"part three, completed! Taking a 2 sec break.\n")
		time.sleep(2)  # Sleep for 2 sec.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to create the protected tag. Response "
		          f"code {admin_protected_tag.status_code}. Step five, part three. - "
		          f"{admin_protected_tag.request.url}\t{admin_protected_tag.request.body}\t{admin_protected_tag.request.headers}\n")
		sys.exit(
			f"Unable to create the protected tag. Response code {admin_protected_tag.status_code}. Step five, part three. -"
			f"{admin_protected_tag.request.url}, {admin_protected_tag.request.body}, {admin_protected_tag.request.headers}")


def check_admin_protected_tag():
	admin_protected_tag = requests.get(
		f"https://platform.{url}/directory/v1/customers/{customer_id}/resourceclasses/users/resources/{get_user()}/tags",
		headers = bearer)
	time.sleep(1)  # Sleep for 1 sec.
	if admin_protected_tag.ok:
		if admin_protected_tag.json()["pageResultSize"] != 0:
			print(f"There is a protected tag for user {get_user()}.")
			log.write(f"[{datetime.datetime.now()}]\tThere is a protected tag for user {get_user()}.\n")
		else:
			print(f"There is no protected tag for the user. Creating one now.")
			log.write(f"[{datetime.datetime.now()}]\tThere is no protected tag for the user. Creating one now.\n")
			create_admin_protected_tag()  # Calling the function to create the admin role.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to execute the GET API request. Response "
		          f"code: {admin_protected_tag.status_code}. Step five, part three. -"
		          f"{admin_protected_tag.request.url}\t{admin_protected_tag.request.body}\t{admin_protected_tag.request.headers}\n")
		sys.exit(f"Unable to execute the GET API request. Step five, part three.")


check_admin_protected_tag()  # Calling the function to check if the user has a protected tag.


# 5 - User DB Validation. Part four.
def master_user_template_payload():
	payload = {
		"templateName": "8x8 Master User Template",
		"customerId": f"{customer_id}",
		"templateType": "USER",
		"template": {
			"fields": [
				{
					"name": "disable_vod_login",
					"value": False,
					"category": "general",
					"description": "The user is not allowed to use VOD",
					"defaultLabel": "Virtual Office Desktop login disabled"
				},
				{
					"name": "disable_vom_login",
					"value": False,
					"category": "general",
					"description": "The user is not allowed to use VOM",
					"defaultLabel": "Virtual Office Mobile login disabled"
				},
				{
					"name": "disable_voo_login",
					"value": False,
					"category": "general",
					"description": "The user is not allowed to use VOO",
					"defaultLabel": "Virtual Office Online login disabled"
				},
				{
					"name": "disable_create_meetings",
					"value": False,
					"category": "general",
					"description": "The user is only allowed to join Virtual Meetings and not allowed to create them.  "
					               "Has no effect if Virtual Meetings is disabled",
					"defaultLabel": "Disable create Virtual Meetings"
				},
				{
					"name": "disable_virtual_meetings",
					"value": False,
					"category": "general",
					"description": "Virtual Meetings is not shown in the clients",
					"defaultLabel": "Disable Virtual Meetings"
				},
				{
					"name": "desktopapp-disable_vod_upgrade_prompt",
					"value": False,
					"category": "general",
					"description": "Do not prompt users with Admin rights to upgrade to the latest version of VOD when available.",
					"defaultLabel": "Disable Virtual Office Desktop upgrade prompt"
				},
				{
					"name": "disable_messaging",
					"value": False,
					"category": "general",
					"description": "Messaging is not shown in the clients",
					"defaultLabel": "Disable Messaging"
				},
				{
					"name": "disable_sms_messaging",
					"value": False,
					"category": "general",
					"description": "SMS messages can not be sent or received.  Has no effect if Messaging is disabled.",
					"defaultLabel": "Restrict sending SMS messages"
				},
				{
					"name": "disable_browse_contacts",
					"value": False,
					"category": "general",
					"description": "Contacts tab is not shown in the clients, so Contact interaction is via search.",
					"defaultLabel": "Disable Browse Contacts"
				},
				{
					"name": "disable_voicemail_download",
					"value": False,
					"category": "general",
					"description": "Voicemails may be played but not downloaded by the clients.",
					"defaultLabel": "Disable Voicemail Download"
				},
				{
					"name": "disable_voicemail_forward",
					"value": False,
					"category": "general",
					"description": "Voicemails may not be forwarded to other internal extensions",
					"defaultLabel": "Disable Voicemail Forwarding"
				},
				{
					"name": "disable_call_recording_delete",
					"value": False,
					"groupName": "general",
					"description": "The user is not allowed to use delete call recordings",
					"defaultLabel": "Do not allow users to delete their call recordings"
				},
				{
					"name": "disable_call_recording_play",
					"value": False,
					"groupName": "general",
					"description": "The user is not allowed to access call recordings",
					"defaultLabel": "Do not allow users to access their call recordings"
				},
				{
					"name": "disable_voicemail_transcription",
					"value": False,
					"groupName": "general",
					"description": "Voicemail transcription is not included with voicemail notification",
					"defaultLabel": "Disable Voicemail Transcription"
				},
				{
					"name": "disable_user_basic_info_edit_ui",
					"value": False,
					"category": "User profile: basic information",
					"description": "The user is not allowed to edit their basic info section in configuration manager",
					"defaultLabel": "Do not allow users to modify their basic information in configuration manager"
				},
				{
					"name": "disable_user_basic_voice_settings_edit_ui",
					"value": False,
					"category": "User profile: voice basic settings",
					"description": "The user is not allowed to edit their voice basic settings section in configuration manager",
					"defaultLabel": "Do not allow users to modify their voice basic settings in configuration manager"
				},
				{
					"name": "disable_user_voicemail_edit_ui",
					"value": False,
					"category": "User profile: voicemail settings",
					"description": "The user is not allowed to edit their voicemail section in configuration manager",
					"defaultLabel": "Do not allow users to modify their voicemail settings in configuration manager"
				},
				{
					"name": "disable_user_external_callerid_edit_ui",
					"value": False,
					"category": "User profile: external caller ID",
					"description": "The user is not allowed to edit their external caller ID section in configuration manager",
					"defaultLabel": " Do not allow users to modify their external caller ID in configuration manager"
				},
				{
					"name": "disable_user_internal_callerid_edit_ui",
					"value": False,
					"category": "User profile: internal caller ID",
					"description": "The user is not allowed to edit their internal caller ID section in configuration manager",
					"defaultLabel": "Do not allow users to modify their internal caller ID in configuration manager"
				},
				{
					"name": "disable_user_call_forwarding_rules_edit_ui",
					"value": False,
					"category": "User profile: call forwarding rules",
					"description": "The user is not allowed to edit their call forwarding section in configuration manager",
					"defaultLabel": "Do not allow users to modify their call forwarding rules in configuration manager"
				},
				{
					"name": "disable_user_moh_edit_ui",
					"value": False,
					"category": " User profile: music on hold",
					"description": "The user is not allowed to edit their music on hold section in configuration manager",
					"defaultLabel": "Do not allow users to modify their music on hold in configuration manager"
				},
				{
					"name": "disable_user_call_recording_settings_edit_ui",
					"value": False,
					"category": "User profile: call recording settings",
					"description": "The user is not allowed to edit their call recording settings section in configuration manager",
					"defaultLabel": "Do not allow users to modify their call recording settings in configuration manager"
				},
				{
					"name": "disable_user_emergency_address_edit_ui",
					"value": False,
					"category": "User profile: emergency address",
					"description": "The user is not allowed to edit their emergency address section in configuration manager",
					"defaultLabel": "Do not allow users to modify their emergency address in configuration manager"
				},
				{
					"name": "disable_user_fax_settings_edit_ui",
					"value": False,
					"category": "User profile: fax settings",
					"description": "The user is not allowed to edit their fax settings section in configuration manager",
					"defaultLabel": "Do not allow users to modify their fax settings in configuration manager"
				},
				{
					"name": "vod_version_to_use",
					"value": "latest",
					"category": "general",
					"description": "The users will not be able to update to a newer VOD version than the specified one",
					"defaultLabel": "Do not allow user to use a Virtual Office desktop version higher than "
				}
			]
		},
		"isDefault": True
	}
	return payload


def create_master_user_template():
	# Creating the main admin.
	master_user_template = requests.post(
		f"https://platform.8x8.com/vo/config/v1/customers/{customer_id}/templates", headers = bearer,
		json = master_user_template_payload())
	if master_user_template.ok:
		print(f"Created the '8x8 Master User Template'. Step five, part four, completed! Taking a 2 sec break.")
		log.write(f"[{datetime.datetime.now()}]\tCreated the '8x8 Master User Template'. Step five, "
		          f"part four, completed! Taking a 2 sec break.\n")
		time.sleep(2)  # Sleep for 2 sec.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to create the '8x8 Master User Template'. Response "
		          f"code {master_user_template.status_code}. Step five, part four. - "
		          f"{master_user_template.request.url}\t{master_user_template.request.body}\t{master_user_template.request.headers}\n")
		sys.exit(
			f"Unable to create the '8x8 Master User Template'. Response code {master_user_template.status_code}. Step "
			f"five, part four. - "
			f"{master_user_template.request.url}, {master_user_template.request.body}, {master_user_template.request.headers}")


def check_master_user_template():
	master_user_template = requests.get(
		f"https://platform.8x8.com/vo/config/v1/customers/{customer_id}/templates", headers = bearer)
	time.sleep(1)  # Sleep for 1 sec.
	if master_user_template.ok:
		if master_user_template.json()["pageResultSize"] != 0:
			print("The '8x8 Master User Template' is already created.")
			log.write(f"[{datetime.datetime.now()}]\tThe '8x8 Master User Template' is already created.\n")
		else:
			print(f"There is no '8x8 Master User Template'. Creating one now.")
			log.write(f"[{datetime.datetime.now()}]\tThere is no '8x8 Master User Template'. Creating one now.\n")
			create_master_user_template()  # Calling the function to create the admin role.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to execute the GET API request. Response "
		          f"code: {master_user_template.status_code}. Step five, part four. -"
		          f"{master_user_template.request.url}\t{master_user_template.request.body}\t{master_user_template.request.headers}\n")
		sys.exit(f"Unable to execute the GET API request. Step five, part four.")


check_master_user_template()  # Calling the function to check if the '8x8 Master User Template' already exists.


# 6 - Admin Validation
def rbac_payload():
	payload = {
		"matchingRule": {
			"name": f"{user_first_name} {user_last_name}",
			"rule": f"userId == \"{get_user()}\""
		},
		"assignments": [
			{
				"application": {
					"name": "configuration-manager"
				},
				"scopes": [
					{
						"id": "02edc0ec-0aa6-483d-8848-e2a517189bf4"
					}
				],
				"roles": [
					{
						"id": "bdf1cf5e-f94d-4b64-8924-17196d6faf40"
					}
				]
			}
		]
	}
	return payload


def create_rbac_permissions():
	# Creating the RBAC permissions.
	headers = {
		'Authorization': 'Bearer ' + authentication(),
		'Content-Type': 'application/json',
		'Rbac-Override-Tenant-Id': f'{customer_id}'
	}
	rbac_permissions = requests.post(
		f"https://cloud8.{url}/rbac/api/v1/admin/composite/multiple/assignments", headers = headers,
		json = rbac_payload())
	if rbac_permissions.ok:
		print(f"Created the admin role for {get_user()}.")
		log.write(f"[{datetime.datetime.now()}]\tCreated the admin role for {get_user()}.\n")
		time.sleep(2)  # Sleep for 2 sec.
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to create the admin role. Response "
		          f"code {rbac_permissions.status_code}. Step six. - "
		          f"{rbac_permissions.request.url}\t{rbac_permissions.request.body}\t{rbac_permissions.request.headers}\n")
		sys.exit(f"Unable to execute the POST API request. Response code {rbac_permissions.status_code}. Step six. - "
		         f"{rbac_permissions.request.url}, {rbac_permissions.request.body}, {rbac_permissions.request.headers}")


def check_rbac_permissions():
	headers = {
		'Authorization': 'Bearer ' + authentication(),
		'Content-Type': 'application/json',
		'Rbac-Override-Tenant-Id': f'{customer_id}'
	}
	user_role = requests.get(
		f'https://cloud8.{url}/rbac/api/v1/admin/assignments?filter=matchingRule.rule=="userId == \\"{get_user()}\\""',
		headers = headers)
	time.sleep(1)  # Sleep for 1 sec.
	if user_role.ok:
		if user_role.json()["content"]:
			print(f"RBAC permissions are present for {get_user()}.")
			log.write(f"[{datetime.datetime.now()}]\tRBAC permissions are present for {get_user()}.\n")
		else:
			print(f"There are no RBAC permissions for the {get_user()}. Creating them now.")
			log.write(
				f"[{datetime.datetime.now()}]\tThere are no RBAC permissions for the {get_user()}. Creating them now.\n")
			create_rbac_permissions()
	else:
		log.write(f"[{datetime.datetime.now()}]\tUnable to execute the GET API request. Response "
		          f"code: {user_role.status_code}. Step six. -"
		          f"{user_role.request.url}\t{user_role.request.body}\t{user_role.request.headers}\n")
		sys.exit(f"Step six. Unable to execute the GET API request. Response code: {user_role.status_code}. Step six. -"
		         f"{user_role.request.url}")


check_rbac_permissions()  # Check RBAC permissions.
log.close()  # Close the log file.
