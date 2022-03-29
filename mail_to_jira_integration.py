#https://pypi.org/project/easyimap/
import easyimap
import json
#https://atlassian-python-api.readthedocs.io/
from atlassian import Jira
import logging

#Credentials for email
user="sre_testing@mail.com"
host="imap.mail.com"
password="Here is my password"
mailbox="inbox"

#credentials for jira
email = "email i use to access Jira"
ticket_automation_new_token="Jira access token"



#Connection to mail
imapper = easyimap.connect(host, user, password)
mail_count = len(imapper.listids(100))
print("There are", mail_count, "mails that haven't created alarms")

#for cloud jira access info : https://atlassian-python-api.readthedocs.io/
jira = Jira(
    url='https://ksiachras.atlassian.net',
    username = email,
    password=ticket_automation_new_token,
    cloud=True
)

#gets the remain mail objects in a dictionary
mails = imapper.listup(mail_count)
for mail in mails:
    data = json.loads(mail.body)
    alarm_title = data["title"]
    mail_description_body = data["body"]
    severity = data["severity"]
    timestamp = data["timestamp"]
    for sub_item in data["alarmMetaData"]:
        status = sub_item["status"]
        oci_uid = sub_item["id"]
        query = sub_item["query"]
    jql_request = 'project = SRE AND issuetype = Issue AND status in (Assigned, "In Progress", Unassigned) AND summary ~ "' +  alarm_title +'"'


#    jql_request = 'project = SRE AND summary ~ ',alarm_title' AND issuetype = Issue AND status in (Assigned, "In Progress", Unassigned)'
    logging.basicConfig(filename='jira_connect.log', filemode='w', level=logging.DEBUG)
    try:
        ticket_exist=0
        issues = jira.jql(jql_request)
        print("found issues in jira:", len(issues["issues"]))
        for issue in issues["issues"]:
            id = issue["id"]
            issue_key = issue["key"]
            summary= issue["fields"]["summary"]
            print("issue tittle is:", summary)
            if summary == alarm_title :
                print("Ticket exists, we will just update ticket_exist value")
                ticket_exist=1
                #TODO Create update comment
        if ticket_exist==1:
            print("Adding a new comment to existing Jira ticket")
            #Just updating the ticket with status from e-mail body descriptions.
            jira.issue_add_comment(issue_key, mail_description_body)

        elif ticket_exist==0:
            print("Creating a new ticket at backlog of SRE project")
            fields = dict(summary=alarm_title,
                          project = dict(key='SRE'),
                          issuetype = dict(name='Issue'),
                          description = mail_description_body
                          )
            jira.issue_create(fields)



    except Exception as e:
        logging.error(e)




imapper.quit()
