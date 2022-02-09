import requests
import sys
import datetime
from config import credentials, url, start_date, end_date

headers = {'Cookie': f'SESSION={credentials}', 'Content-Type': 'text/plain', 'AUTH_TYPE': 'BASE',
		   'auth-secret': '48924jfn3459hf54fm4hf88!#%^%&*()_$'}  # Headers for the DELETE API request.

log = open("apis.log", "a")  # Logging all API requests.
file = open("recordings.txt", "r")  # Licenses to be removed.

if not log.writable():  # Checking if we can write the log file.
	print("Cannot write the log file.")
	sys.exit()

if not file.readable():  # Checking if we can read the text file.
	print("Cannot read the text file.")
	sys.exit()

confirmation = input(f"Do you want to remove all recordings from the text file for {credentials}? Enter Y or N: ")

count = 0  # Counter for all licenses removed.

start_time = datetime.datetime.now()  # Time it started to remove licenses.

if confirmation in ["Y", "y"]:
	for row in file.readlines():
		a_recording = row.strip("\n")  # Recordings from the text file, one at a time.
		# SQL query command for deleting each recording from the text file.
		data = f'"createdAt" BETWEEN ("{start_date}", "{end_date}") AND "transactionNum" IN ("{a_recording}")'
		remove_recording = requests.delete(
			f"https://uk.rec.{url}/api/calls/purge_by_query", headers=headers, data=data)
		if remove_recording.ok:
			print(f"{a_recording} removed for {credentials}.")
			count += 1
			log.write(
				f"[{datetime.datetime.now()}]\tDELETE {remove_recording.request.url}\t{a_recording} removed "
				f"for {credentials}\t{remove_recording.request.body}\n")
		else:
			print(f"Unable to run the DELETE API request. Status code {remove_recording.status_code}.")
			log.write(f"{datetime.datetime.now()}\tUnable to run the DELETE API request. Status code "
					  f"{remove_recording.status_code}\tAPI request {remove_recording.request.url}\t"
					  f"Body API request {remove_recording.request.body}\n")
	end_time = datetime.datetime.now()  # Time it ended.
	time_elapsed = end_time - start_time  # Time it took to run the script successfully for all licenses.
	print(f"{count} licenses removed in {time_elapsed}.")
	log.write(f"[{datetime.datetime.now()}]\t{count} licenses removed in {time_elapsed}.\n")
else:
	print("Operation cancelled.")
	sys.exit()

file.close()
log.close()
