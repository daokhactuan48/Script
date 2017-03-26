from __future__ import print_function
import httplib2
import os

import email
import requests
import sys
import json
import base64

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

def get_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build ('gmail', 'v1', http=http)
    return service

def get_id_label(name_label):
    service = get_service()
    repond_id_label=service.users().labels().list(userId="me").execute()
    list_id_label = repond_id_label["labels"]
    for id_label in list_id_label:
            if id_label["name"] == name_label:
                    return id_label["id"]

def get_list_id_message_new(name_label,number_message_new):
    label_id = get_id_label(name_label)
    service = get_service()
    respond_id_message=service.users().messages().list(userId="me",labelIds=label_id,maxResults=number_message_new).execute()
    list_id = []
    list_id.extend(respond_id_message['messages'])
    return list_id

def get_all_mess(name_label):
    id_label = get_id_label(name_label)
    service = get_service()
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

def move_mail(id_thread,name_label,name_label_readed):
    id_name_label = get_id_label(name_label)
    id_name_label_readed = get_id_label(name_label_readed)
    request_body = {
	    'removeLabelIds': id_name_label,
		'addLabelIds': id_name_label_readed
	}
	service = get_service()
    thread = service.users().threads().modify(userId="me",id=id_thread,body=request_body)
	
def Sum_all_mail(name_label):
    messages = get_id_all_mess(get_id_label(name_label));
    total = 0;
    for id_message in messages:
       total +=1
    return total

def store_total_mail(name_label,total_mail):
    path = "/root/gmailapi/total_mail/"
    path = path + name_label
    file = open(path,"w")
    file.write(str(total_mail))
    file.close()

def get_subject(id_message):
    service = get_service()
    respond_subj = service.users().messages().get(userId="me",id=id_message).execute()
    for id_subject in respond_subj["payload"]["headers"]:
        if id_subject["name"] == "Subject":
                    return  (id_subject["value"])

def get_Mime_Message(id_message):
    service = get_service()
    respond_subj = service.users().messages().get(userId="me",id=id_message).execute()
#    print (respond_subj['payload']['body'])
    msg_str = base64.urlsafe_b64decode(respond_subj['payload']["body"]["data"].encode('ASCII'))
    path = "/root/gmailapi/mail/" + "test.txt" + id_message
    file = open(path,"w")
    file.write(msg_str)
    file.close()


def check_file_attachment(id_message):
    service = get_service()
    respond_subj = service.users().messages().get(userId="me",id=id_message).execute()
    if 'data' in respond_subj['payload']['body']:
        return True
    else:
        return False

def get_content_mess(id_message,path):
    service = get_service()
    respond_content = service.users().messages().get(userId="me",id=id_message).execute()
    path = path + "mail.txt"
    if check_file_attachment(id_message) == True:
        mes_str = base64.urlsafe_b64decode(respond_content["payload"]["body"]["data"].encode('ASCII'))
        file = open(path,"w")
        file.write(mes_str)
        file.close()
    else:
        att_id = respond_content["payload"]["body"]["attachmentId"]
        att=service.users().messages().attachments().get(userId=user_id, messageId=msg_id,id=att_id).execute()
        data=att['data']
        file = open(path,"w")
        file.write(data)
        file.close()
    return path

def read_file(pathfile):
    file = open(pathfile,"r")
    for line in iter(file):
        print (line)
    file.close()

class Email_content(object):
    def __init__(self,Service,Host,Address,State,AdditionalInfo):
        self.Service = Service
        self.Host = Host
        self.Address = Address
        self.State = State
        self.AdditionalInfo = AdditionalInfo
    def get_Service (self):
        return self.Service
    def get_Host (self):
        return self.Host
    def get_Address (self):
        return self.Address
    def get_State(self):
        return self.State
    def get_AdditionalInfo (self):
        return self.AdditionalInfo

def hipchat_notify(token,room,message, color='yellow', notify=False,
                   format='text', host='api.hipchat.com'):
    url = "https://{0}/v2/room/{1}/notification".format(host, room)
    headers = {'Content-type': 'application/json'}
    headers['Authorization'] = "Bearer " + token
    payload = {
        'message': message,
        'notify': notify,
        'message_format': format,
        'color': color
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
		
def get_content_email(list_id,path,token,room):
    for id in list_id:
        if "IS WARNING" in get_subject(id['id']):
            continue
        else:
            pathfile = get_content_mess (id['id'],path)
            file = open(pathfile,"r")
            for line in iter(file):
                if "Notification Type" in line:
                    continue
                elif "Service" in line:
                    substring = line.split(':')
                    Service = substring[1]
                elif "Host" in line:
                    substring = line.split(':')
                    Host = substring[1]
                elif "Address" in line:
                    substring = line.split(':')
                    Address = substring[1]
                elif "State" in line:
                   substring = line.split(':')
                   State = substring[1]
                elif "Additional Info" in line:
                   substring = line.split('Info :')
                   Additional = substring[1]
                else:
                    continue
            email_content = Email_content(Service,Host,Address,State,Additional)	
            hipchat_notify(token,room,email_content.get_AdditionalInfo())

			
			
if __name__ == '__main__':
    name_label = "1.6.TRS_Centreon-enginge"
    name_label_readed = "1.6.TRS_Centreon-enginge_READED"
    number_message_new = 10
    path = "/root/gmailapi/mail/"
    list_id = get_list_id_message_new(name_label,number_message_new)
    for id in list_id:
        move_mail(id["threadId"],name_label,name_label_readed)
