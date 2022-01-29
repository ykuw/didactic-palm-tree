#!/usr/bin/python3.6

import mysql.connector
import time
import sys

try:
    db1 = mysql.connector.connect(
        host="",
        user="",
        passwd="",
        database=""
    )

    num_count = int(input("Number of requested telephone numbers: "))
    prefix = input("Enter the prefix with a leading 0: ")
    ccid = int(input("Enter the ccid: "))
    cid = int(input("Enter the cid: "))
    case_num = input("Enter case number: ")
    silo = int(input("Enter silo (103, 106 only): "))

    silos = (103, 106)

    db2 = mysql.connector.connect(
        host=f"db{silo}",
        user="",
        passwd="",
        database=f"db{silo}"
    )

    cursor1 = db1.cursor()
    cursor1.execute(f"SELECT * FROM numbers WHERE ddi LIKE '{prefix}%' AND mode = 'queue' AND "
                    f"carrier NOT LIKE '%gamma%' AND silo NOT IN (103, 106, 107) AND ccid = 0 AND "
                    "internal_notes NOT LIKE '%t-point%'"
                    f"LIMIT {num_count}")
    rows = cursor1.fetchall()

    file = open(f"log/{case_num}.log", "a")

    if file.writable():
        file.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\t" + str(rows))
        file.write("\n")
    else:
        print("\nUnable to write to the log file. The operation has been canceled.")
        sys.exit()

    cursor2 = db2.cursor()

    if silo in silos:
        if cursor1.rowcount > 0:
            if num_count > cursor1.rowcount:
                print(f"\n{cursor1.rowcount} results returned, fewer than requested. Operation canceled.\n")
                sys.exit()
            else:
                do_all = input("\nInsert all in one go? ")
                if do_all in ["Y", "y"]:
                    for row in rows:
                        cursor2.execute("INSERT INTO numbers (ddi, silo, ccid, campaign, assigned, allocated, "
                                        "internal_notes, client_notes, agentid, carrier, alias, qid) VALUES "
                                        f"('{row[1]}', {silo}, {ccid}, {cid}, NOW(), NOW(), '{case_num}', '', 0, "
                                        f"'{row[13]}', '', 0) "
                                        "ON DUPLICATE KEY UPDATE "
                                        "silo = VALUES (silo), "
                                        "ccid = VALUES (ccid), "
                                        "campaign = VALUES (campaign), "
                                        "internal_notes = VALUES (internal_notes), "
                                        f"qid = VALUES (qid);")
                        file.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\t" + cursor2.statement)
                        file.write("\n")
                        cursor1.execute(f"UPDATE numbers SET silo = {silo}, internal_notes = '{case_num}', "
                                        "allocated = NOW(), status = 'Used' "
                                        f"WHERE ddi = '{row[1]}'")
                        file.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\t" + cursor1.statement)
                        file.write("\n")
                        print(f"{row[1]} successfully allocated to cid {cid}, ccid {ccid} on silo {silo}.")
                    db1.commit()
                    db2.commit()
                else:
                    for row in rows:
                        say_yn = input(f"\n{row[1]} has been found on our system. Do you want to continue? Y for yes, any key for no: ")
                        if say_yn in ["Y", "y"]:
                            cursor2.execute("INSERT INTO numbers (ddi, silo, ccid, campaign, assigned, allocated, "
                                            "internal_notes, client_notes, agentid, carrier, alias, qid) VALUES "
                                            f"('{row[1]}', {silo}, {ccid}, {cid}, NOW(), NOW(), '{case_num}', '', 0, "
                                            f"'{row[13]}', '', 0) "
                                            "ON DUPLICATE KEY UPDATE "
                                            "silo = VALUES (silo), "
                                            "ccid = VALUES (ccid), "
                                            "campaign = VALUES (campaign), "
                                            "internal_notes = VALUES (internal_notes), "
                                            f"qid = VALUES (qid);")
                            file.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\t" + cursor2.statement)
                            file.write("\n")
                            cursor1.execute(f"UPDATE numbers SET silo = {silo}, internal_notes = '{case_num}', "
                                            "allocated = NOW() "
                                            f"WHERE ddi = '{row[1]}'")
                            file.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\t" + cursor1.statement)
                            file.write("\n")
                            print(f"{row[1]} successfully allocated to cid {cid}, ccid {ccid} on silo {silo}.")
                        else:
                            print("\nThe operation has been canceled.\n")
                            sys.exit()
                    db1.commit()
                    db2.commit()
        else:
            print(f"\nNo results for prefix {prefix}. Please, place an order to BT.\n")
    else:
        print("\nEnter either silo 103 or 106.\n")

        file.close()
        cursor1.close()
        cursor2.close()
        db1.close()
        db2.close()

except (ValueError, NameError):
    print("\nEnter an integer for all questions, except case number.\n")
except PermissionError:
    print("\nUnable to write the log file.\n")