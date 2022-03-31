import mysql.connector
import sys
import datetime

start_range = int(input("Enter start range: "))
end_range = int(input("Enter end range: "))
geographic_location = input("Enter geographic location: ")
silo = input("Enter silo: ")
case_number = input("Enter case number: ")

db1 = mysql.connector.connect(
    host="",
    user="",
    passwd="",
    database=""
)

db2 = mysql.connector.connect(
    host=f"db{silo}",
    user="",
    passwd="",
    database=f"db{silo}"
)

cursor1 = db1.cursor()
cursor2 = db2.cursor()

sequences = []
remainder_list = []


def split_numbers(start, end):
    last_digit = 0  # Last digit of the sequence.
    for number in range(start, end):  # Iterate through the numbers.
        if number % 10 == last_digit:  # If the last digit is the same as the current number's last digit.
            last_digit += 1  # Increment last digit.
        if last_digit == 9:  # If last digit is 9, reset to 0.
            sequences.append(number // 10)  # Append the first digit of the number.
            last_digit = 0  # Reset last digit to 0.

    for number in range(start, end + 1):
        if number not in range(sequences[0] * 10, sequences[-1] * 10 + 10):
            remainder_list.append(number)


split_numbers(start_range, end_range)

question = input(f"Numbers between {start_range} and {end_range} to insert in the db? ")

file = open(f"log/{case_number}_bt.log", "a")

if file.writable():
    if question in ["Y", "y"]:
        if start_range % 100 == 0:  # If the start range is a multiple of 100, insert the numbers in the db.
            for number in range(start_range, end_range + 1):
                cursor1.execute("INSERT INTO `numbers` (`ddi`, `silo`, `ccid`, `campaign`, `qid`, `agentid`, "
                                "`assigned`, "
                                "`allocated`, `mode`, `status`, `internal_notes`, `client_notes`, `carrier`, `alias`, "
                                "`ppm_day`, "
                                "`ppm_eve`, `ppm_weekend`, `cost_day`, `cost_eve`, `cost_weekend`, `999_contact_id`, "
                                "`999_sync`, "
                                "`999_note`, `999_confirm`) "
                                f"VALUES ('0{number}', {silo}, '0', '0', '0', '0', NOW(), NOW(), 'queue', 'Available', "
                                f"'{case_number}', '', '', '', '0', '0', '0', '0', '0', '0', NULL, NULL, NULL, NULL)")
                db1.commit()  # Commit the changes.
                file.write(f"{datetime.datetime.now()} \t {cursor1.statement}")
                file.write("\n")

            double_zero_start_range = start_range // 100  # Get the first digit of the start range.

            cursor2.execute("INSERT INTO `numbers_blocks` (`silo`, `intprefix`, `natprefix`, `block`, `suffixlen`, "
                                "`prefix`, `e164prefix`, `tariff_type`, `description`, `added`, `source`, "
                            "`setup_price`, "
                                "`rental_price`, `allocate`, `available`, `per_call_day`, `per_call_eve`, "
                            "`per_call_weekend`, "
                                "`per_min_day`, `per_min_eve`, `per_min_weekend`, `routable`, `automatic_allocation`) "
                                f"VALUES ({silo}, '44', '0', {double_zero_start_range}, '2', '0{double_zero_start_range}', '44{double_zero_start_range}', "
                                f"'Landline Standard', '{geographic_location}', NOW(), 'ofcom', '200', '100', 'yes', "
                                "'100', '0', '0', '0', '0.0048', '0.0048', '0.0048', 'yes', '0')")
            db2.commit()  # Commit the changes.
            file.write(f"{datetime.datetime.now()} \t {cursor2.statement}")
            file.write("\n")
        else:
            for number in range(start_range, end_range + 1):
                cursor1.execute("INSERT INTO `numbers` (`ddi`, `silo`, `ccid`, `campaign`, `qid`, `agentid`, "
                                "`assigned`, "
                                "`allocated`, `mode`, `status`, `internal_notes`, `client_notes`, `carrier`, `alias`, "
                                "`ppm_day`, "
                                "`ppm_eve`, `ppm_weekend`, `cost_day`, `cost_eve`, `cost_weekend`, `999_contact_id`, "
                                "`999_sync`, "
                                "`999_note`, `999_confirm`) "
                                f"VALUES ('0{number}', {silo}, '0', '0', '0', '0', NOW(), NOW(), 'queue', 'Available', "
                                f"'{case_number}', '', '', '', '0', '0', '0', '0', '0', '0', NULL, NULL, NULL, NULL)")
                db1.commit()  # Commit the changes.
                file.write(f"{datetime.datetime.now()} \t {cursor1.statement}")
                file.write("\n")

            for sequence in sequences:
                cursor2.execute("INSERT INTO `numbers_blocks` (`silo`, `intprefix`, `natprefix`, `block`, `suffixlen`, "
                                "`prefix`, `e164prefix`, `tariff_type`, `description`, `added`, `source`, `setup_price`, "
                                "`rental_price`, `allocate`, `available`, `per_call_day`, `per_call_eve`, `per_call_weekend`, "
                                "`per_min_day`, `per_min_eve`, `per_min_weekend`, `routable`, `automatic_allocation`) "
                                f"VALUES ({silo}, '44', '0', {sequence}, '1', '0{sequence}', '44{sequence}', "
                                f"'Landline Standard', '{geographic_location}', NOW(), 'ofcom', '200', '100', 'yes', "
                                "'10', '0', '0', '0', '0.0048', '0.0048', '0.0048', 'yes', '0')")
                db2.commit()  # Commit the changes.
                file.write(f"{datetime.datetime.now()} \t {cursor2.statement}")
                file.write("\n")

            for remainder in remainder_list:
                cursor2.execute("INSERT INTO `numbers_blocks` (`silo`, `intprefix`, `natprefix`, `block`, `suffixlen`, "
                                "`prefix`, `e164prefix`, `tariff_type`, `description`, `added`, `source`, `setup_price`, "
                                "`rental_price`, `allocate`, `available`, `per_call_day`, `per_call_eve`, `per_call_weekend`, "
                                "`per_min_day`, `per_min_eve`, `per_min_weekend`, `routable`, `automatic_allocation`) "
                                f"VALUES ({silo}, '44', '0', {remainder}, '1', '0{remainder}', '44{remainder}', "
                                f"'Landline Standard', '{geographic_location}', NOW(), 'ofcom', '200', '100', 'yes', "
                                "'1', '0', '0', '0', '0.0048', '0.0048', '0.0048', 'yes', '0')")
                db2.commit()  # Commit the changes.
                file.write(f"{datetime.datetime.now()} \t {cursor2.statement}")
                file.write("\n")
    else:
        sys.exit("Exiting the script.")
else:
    sys.exit("Unable to write to the file. Exiting the script.")

cursor1.close()
cursor2.close()
db1.close()
db2.close()
