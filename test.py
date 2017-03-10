from __future__ import print_function
import httplib2
import os


import requests
import sys
import json

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret_nta.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'credentialv1.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

#def total_mess_pl():
#    credentials = get_credentials()
#    http = credentials.authorize(httplib2.Http())
#    service = discovery.build ('gmail', 'v1', http=http)
#    respond_id_message=service.users().messages().list(userId="me",labelIds="Label_7").execute()
#    total_mess = 0 + respond_id_message["resultSizeEstimate"]	
#    while 'nextPageToken' in respond_id_message:
#        page_token = respond_id_message['nextPageToken']
#        respond_id_message = service.users().messages().list(userId="me",
#                                                 labelIds="Label_7",
#                                                 pageToken=page_token).execute()
#        total_mess += respond_id_message["resultSizeEstimate"]
#    return total_mess
	
def get_id_message_news(name_label):
    label_id = get_id_label(name_label)
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build ('gmail', 'v1', http=http)
    repond_id_message=service.users().messages().list(userId="me",labelIds=label_id,maxResults=1).execute()
    return repond_id_message["messages"][0]["id"]

def get_id_label(name_label):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build ('gmail', 'v1', http=http)
    repond_id_label=service.users().labels().list(userId="me").execute()
    list_id_label = repond_id_label["labels"]
    for id_label in list_id_label:
	    if id_label["name"] == name_label:
		    return id_label["id"]
            
def get_id_all_mess(id_label):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build ('gmail', 'v1', http=http)
    repond_id_message=service.users().messages().list(userId="me",labelIds=id_label).execute()
    messages = []
    if 'messages' in repond_id_message:
        messages.extend(repond_id_message['messages'])
    while 'nextPageToken' in repond_id_message:
      page_token = repond_id_message['nextPageToken']
      repond_id_message = service.users().messages().list(userId="me",
                                                 labelIds=id_label,
                                                 pageToken=page_token).execute()
      messages.extend(repond_id_message['messages'])
    return messages	  

def Sum_all_mail(name_label):
    messages = get_id_all_mess(get_id_label(name_label));
    total = 0;
    for id_message in messages:
       total +=1
    return total  

def store_total_old_PL(total_old_PL):
    ten_file = "total_mail_PL.txt"	
    file = open(ten_file,"w")
    file.write(str(total_old_PL))
    file.close()

def store_total_old_BO(total_old_BO):
    ten_file = "total_mail_BO.txt"
    file = open(ten_file,"w")
    file.write(str(total_old_BO))
    file.close()

def Compare_mail(name_label):
    if name_label =="1.2.TRS_PL_MAIL_DAILY/TRS_PL_MAIL_BO" or name_label=="1.2.TRS_PL_MAIL_DAILY/TRS_PL_MAIL":
        if name_label == "1.2.TRS_PL_MAIL_DAILY/TRS_PL_MAIL_BO":
            file = open("total_mail_BO.txt","r")
            total_old = file.read()
            file.close()
            if Sum_all_mail(name_label) > int(total_old):
                return True
            else:
                return False
        if name_label == "1.2.TRS_PL_MAIL_DAILY/TRS_PL_MAIL":
            file = open("total_mail_PL.txt","r")
            total_old = file.read()
            file.close()
            if Sum_all_mail(name_label) > int(total_old):
               return True
            else:
               return False			
## Function show Subject of Message 
def get_subject(id_message):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build ('gmail', 'v1', http=http)
    respond_subj = service.users().messages().get(userId="me",id=id_message).execute()
    for id_subject in respond_subj["payload"]["headers"]:
        if id_subject["name"] == "Subject":
		    print  (id_subject["value"])


def hipchat_notify(token, message, color='yellow', notify=False,
                   format='text', host='tuandk.hipchat.com'):
    url = "https://tuandk.hipchat.com/v2/room/3657870/notification"
#PRO    url = "https://nextopasia.hipchat.com/v2/room/1494538/notification"
    headers = {'Content-type': 'application/json'}
    headers['Authorization'] = "Bearer " + token
    payload = {
        'message': message,
        'notify': notify,
        'message_format': format,
        'color': color
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
			
if __name__ == '__main__':
    name_label = "1.2.TRS_PL_MAIL_DAILY/TRS_PL_MAIL"
#    get_subject(get_id_message_news(name_label))
#    token = "HoihlJx6zgLbhSAoBcpMr7zE5BCuayGSBlcsvF6U"
#    name_label = "1.2.TRS_PL_MAIL_DAILY/TRS_PL_MAIL_BO"
#    get_subject(get_id_message_news(name_label))
#    Compare_mail(name_label)
    if Compare_mail(name_label) == True:
	   print (get_subject(get_id_message_news(name_label)))
	   store_total_old_PL(Sum_all_mail(name_label))
    else: 
	   print ("ERROR, Please check")
## TOKEN PRO
#    token = "jVUefN8VIpA29tnX7CdXnsMfrgZgFMbWBehGbM4O"
#    message = get_subject(get_id_message_news(name_label))
#    hipchat_notify(token,message)
#    name_label = "1.2.TRS_PL_MAIL_DAILY/TRS_PL_MAIL"
#    message = get_subject(get_id_message_news(name_label))
#    hipchat_notify(token,message) 
#    name_label = "1.3.TRS_AUTO_KESHIKOMI"
#    message = get_subject(get_id_message_news(name_label))
#    hipchat_notify(token,message)
	#    print ("Tong so mail:",Sum_all_mail(name_label))
#    list_id_mess = get_id_all_mess();
#    total = 0;
#    for id_message in list_id_mess:
#       get_subject(id_message["id"])
#       total +=1
#    print ("Tong so mail", total)
#    id_message_pl = get_id_message_news_pl();
#    get_subject(id_message_pl)
#    print (total_mess_pl())
#    id_message_bo = get_id_message_news_bo();
#    get_subject(id_message_bo)
#    print (total_mess_bo())