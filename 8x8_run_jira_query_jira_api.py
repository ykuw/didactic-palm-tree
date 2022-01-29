from atlassian import Jira
import json

# JQL = 'project =  AND status NOT IN (Closed, Resolved) ORDER BY issuekey'
JQL = 'id = "PLAT-8714"'

jira = Jira(url="", username="", password="")

data = jira.jql(JQL)

# for ceva in data['issues']:
# 	print("Assignee: " + ceva['fields']['assignee']['name'])
# 	print("Status: " + ceva['fields']['status']['name'])
# 	for ceva1 in ceva['fields']['components']:
# 		print("Component: " + ceva1['name'])

JQL2 = 'issuetype != Bug AND status != Closed AND project != "Feature Requests"'

tickets = jira.jql(JQL2)

print(tickets)

# for ticket in tickets['issues']:
# 	print(ticket['key'])
