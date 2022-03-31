import sys
import os
import datetime

try:

    cid = int(input("Enter cid: "))
    start_date = input("Enter start date in YYYY-MM-DD HH:MM:SS format: ")
    end_date = input("Enter end date in YYYY-MM-DD HH:MM:SS format: ")
    choose = int(input("Enter 1 to get CDR or any other number to get connection dates: "))

    file = open("ico.txt", "r")

    log = open("ico.log", "w")

    if not log.writable():  # Checking if we can write the log file.
        sys.exit("The log file is not writable. Exiting the script.")

    if not file.readable():  # Checking if we can read the text file.
        sys.exit("The text file is not readable. Exiting the script.")

    for row in file.readlines():
        ddi = row.strip("\n")
        if choose == 1:
            print(f"Obtaining data for {ddi}.")

            query = "SELECT c.DDI, c.CLI, c.datetime AS Timestamp, c.duration AS Duration, c.result AS Result " \
                    "FROM calls c " \
                    f"JOIN queues q ON q.uid = c.qid AND q.grouping = {cid} AND q.type = 'outbound' " \
                    f"WHERE c.datetime BETWEEN '{start_date}' AND '{end_date}' AND " \
                    f"c.CLI = '{ddi}' AND " \
                    "c.result IN ('Answered', 'TPT') -- c.call_outcome NOT IN ('101', '102') AND "

            os.system(f"echo \"{query}\" | mysql -h -u "
                      f"-p db | sed 's/\t/,/g' > ico/{ddi}.csv")

            print(f"Operation completed for {ddi}.\n")

            log.write(f"[{datetime.datetime.now()}]\t{query}")
        else:
            print(f"Obtaining data for {ddi}.")

            query = "SELECT c.CLI, MIN(c.datetime) AS StartDate, MAX(c.datetime) AS EndDate " \
                    "FROM calls c " \
                    "JOIN queues q ON q.uid = c.qid " \
                    f"WHERE q.grouping = {cid} AND q.type = 'outbound' AND " \
                    f"c.datetime BETWEEN '{start_date}' AND '{end_date}' AND c.CLI = '{ddi}'"

            os.system(f"echo \"{query}\" | mysql -h -u "
                      f"-p db | sed 's/\t/,/g' > ico/{ddi}.csv")

            print(f"Operation completed for {ddi}.\n")

            log.write(f"[{datetime.datetime.now()}]\t{query}")

    file.close()
    log.close()

except AttributeError:
    print("\nUnable to read file.\n")
except FileNotFoundError:
    print("\nFile not found.\n")
except ValueError:
    print("\nEnter a valid character. Please follow the criteria.\n")
