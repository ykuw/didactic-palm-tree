from simple_salesforce import Salesforce
import requests

headers = {"Content-Type": "application/x-www-form-urlencoded"}

body = {
    "username": "",
    "password": "",
    "securityToken": "",
}

token = requests.request(
    url="http://salesforce-case-status.dxi.eu/salesforcelogin",
    method="POST",
    data=body,
    headers=headers,
)

sf = Salesforce(
    instance_url="https://8x8.my.salesforce.com",
    session_id=token.json()["data"]["connection"]["accessToken"],
)

# what = sf.query("SELECT Id, "
#                 "Name, "
#                 "Title "
#                 "FROM User "
#                 "WHERE User_Manager__c = 'Christian Augustine' AND "
#                 "IsActive = True")

# Get GAS members and number of solved gases
query1 = sf.query(
    "SELECT OwnerId, COUNT(CaseNumber) "
    "FROM Case "
    "WHERE OwnerId IN ('0052J000007pB88QAE', '005500000071TWiAAM', '005500000071TgIAAU', "
    "'00550000007gUDpAAM', '0052J000007p0paQAA', '005500000071TOvAAM', '005500000071TblAAE', "
    "'005500000071TbxAAE', '005500000071TgqAAE', '005500000071TcNAAU', '00550000007hIURAA2', "
    "'005500000071TdLAAU', '005500000071ZRlAAM') AND "
    "Status NOT IN ('Customer Requested Hold', 'Escalated', 'Feature Request', 'In Progress', "
    "'In Progress - Customer Responded', 'Pending Customer Response', 'Waiting on Release')"
    "GROUP BY OwnerId"
)

members = {}

# Get names for OwnerId, so we know for which agent the numbers corespond to
query2 = sf.query(
    "SELECT Id, Name "
    "FROM User "
    "WHERE Id IN ('0052J000007pB88QAE', '005500000071TWiAAM', '005500000071TgIAAU', "
    "'00550000007gUDpAAM', '0052J000007p0paQAA', '005500000071TOvAAM', '005500000071TblAAE', "
    "'005500000071TbxAAE', '005500000071TgqAAE', '005500000071TcNAAU', '00550000007hIURAA2', "
    "'005500000071TdLAAU', '005500000071ZRlAAM') "
)

for member in query2["records"]:
    members[member["Id"]] = member["Name"]

# print(members['005500000071TdLAAU'])

# Statuses for GAS tickets
# what = sf.query("SELECT Status, COUNT(CaseNumber) "
#                 "FROM Case "
#                 "WHERE Provider_Group__c = 'Global Application Support Team' "
#                 "GROUP BY Status ")
# for i in what['records']:
# 	print(i)

# OwnerId and number of solved cases, need to add the name of the agent
solved_cases_members = {}

for row in query1["records"]:
    solved_cases_members[row["OwnerId"]] = row["expr0"]
    # solved_cases_members.append(row['OwnerId'] + " " + str(row['expr0']))

# Printing GAS members and their solved cases
# for member in members:
# 	for member1 in solved_cases_members:
# 		if member == member1:
# 			print(members[member] + ": " + str(solved_cases_members[member1]))

# print(solved_cases_members)

# Get resolved cases for the past 2 weeks
query3 = sf.query(
    "SELECT OwnerId, COUNT(CaseNumber) "
    "FROM Case "
    "WHERE OwnerId IN ('0052J000007pB88QAE', '005500000071TWiAAM', '005500000071TgIAAU', "
    "'00550000007gUDpAAM', '0052J000007p0paQAA', '005500000071TOvAAM', '005500000071TblAAE', "
    "'005500000071TbxAAE', '005500000071TgqAAE', '005500000071TcNAAU', '00550000007hIURAA2', "
    "'005500000071TdLAAU', '005500000071ZRlAAM') AND "
    "Status = 'Resolved' "
    "GROUP BY OwnerId"
)

resolved_cases = {}

for row in query3["records"]:
    resolved_cases[row["OwnerId"]] = row["expr0"]

for what in resolved_cases:
    for member in members:
        for m3 in solved_cases_members:
            if member == what == m3:
                print(
                    members[member]
                    + " "
                    + str(resolved_cases[what])
                    + " "
                    + str(solved_cases_members[m3])
                )
                # print(sorted(members[member] + " " + str(resolved_cases[what]) + " " + str(solved_cases_members[m3])))

# print(members)

# for member in members:
# 	for member1 in solved_cases_members:
# 		for member2 in resolved_cases:
# 			if member == member1:
# 				print(members[member] + ": " + str(solved_cases_members[member1]) + ", " + str(resolved_cases[member2]))

# Get description of table (User, Case etc.)
# dct = sf.Case.describe()
# print(dct['fields'])
