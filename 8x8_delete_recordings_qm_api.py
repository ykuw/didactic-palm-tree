import requests
import sys
import datetime
from config import credentials, url, start_date, end_date


if not credentials:  # Check if credentials are defined.
	sys.exit("No credentials provided. Exiting the script.")

if not url:  # Check if url is defined.
	sys.exit("No URL provided. Exiting the script.")

if not start_date:  # Check if start_date is defined.
	sys.exit("No start_date provided. Exiting the script.")

if not end_date:  # Check if end_date is defined.
	sys.exit("No end_date provided. Exiting the script.")


headers = {'Cookie': f'SESSION={credentials}', 'Content-Type': 'text/plain', 'AUTH_TYPE': 'BASE',
		   'auth-secret': '48924jfn3459hf54fm4hf88!#%^%&*()_$'}  # Headers for the DELETE API request.

log = open("apis.log", "a")  # Logging all API requests.
file = open("recordings.txt", "r")  # Licenses to be removed.

if not log.writable():  # Checking if we can write the log file.
	sys.exit("Cannot write to log file. Exiting the script.")

if not file.readable():  # Checking if we can read the text file.
	sys.exit("Cannot read from text file. Exiting the script.")

confirmation = input(f"Do you want to remove all recordings from the text file for {credentials}? Enter Y or N: ")

count = 0  # Counter for all licenses removed.

start_time = datetime.datetime.now()  # Time it started to remove licenses.


# Function to get batches of 1000 rows from the text file.
# Work in progress.
def get_batch(file):
	batch = []
	for i in range(1000):
		line = file.readline()
		if line:
			batch.append(line)
		else:
			break
	return batch


# Function to get 1000 rows at a time from the text file.
# Work in progress.
def get_recordings(file):
	batch = get_batch(file)
	while batch:
		yield batch
		batch = get_batch(file)


if confirmation in ["Y", "y"]:
	for row in file.readlines():
		a_recording = row.strip("\n")  # Recordings from the text file, one at a time.
		# SQL query command for deleting each recording from the text file.
		data = f'"createdAt" BETWEEN ("{start_date}", "{end_date}") AND "transactionNum" IN ("{a_recording}")'
		remove_recording = requests.delete(
			f"https://uk.rec.{url}/api/calls/purge_by_query", headers=headers, data=data)
		if remove_recording.ok:
			print(f"{a_recording} removed for {credentials}.")
			count += 1  # Counting the number of recordings removed.
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
	log.write(f"[{datetime.datetime.now()}]\tExiting the script.\n")
	sys.exit("Exiting the script.")

file.close()
log.close()
