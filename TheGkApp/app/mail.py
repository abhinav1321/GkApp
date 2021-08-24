from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


import base64
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio


SCOPES = ['https://mail.google.com/']
class Main:

    def __init__(self):
        self.creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('/home/abhinav/credentials/token.pickle'):
            with open('/home/abhinav/credentials/token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '/home/abhinav/credentials/credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('/home/abhinav/credentials/token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('gmail', 'v1', credentials=self.creds)


class CreateAndSend:

    def __init__(self,service, to, sender, user_id, subject, message_text):

        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['bcc'] = 'sharmaabhinav97@gmail.com'
        message['subject'] = subject
        to_send = {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}
        print(message)

        try:
            to_send = (service.users().messages().send(userId=user_id, body=to_send)
                       .execute())
            print('Message Id: %s' % to_send['id'])

        except Exception as e:
            print('An error occurred', e)

main = Main()
service = main.service
to = 'abhinavsharma150@gmail.com'
sender = 'mailstream99@gmail.com'
user_id = 'mailstream99@gmail.com'
subject = 'Go Corona, Corona Go'
message_text = 'Hi Users,  That Mail was sent as fun, With Nohup!'


def send_otp_mail(to, subject, message_text):
    CreateAndSend(service, to, sender, user_id, subject, message_text)



