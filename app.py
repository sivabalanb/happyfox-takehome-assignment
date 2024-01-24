# Authenticate to Google’s Gmail API using OAuth fetch a list of emails from your Inbox. Do NOT use IMAP.
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Initialize the service variable as a global variable
service = None

def authenticate_gmail():
    global service

    # If service is already initialized, return it
    if service:
        return service

    # Load the credentials from the credentials.json file
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/gmail.modify'])
    credentials = flow.run_local_server(port=0)

    # Save the credentials for future use
    with open('token.json', 'w') as token_file:
        token_file.write(credentials.to_json())

    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=credentials)

    return service

# Mark a mail as read or unread using the message_id    
def mark_email_read_or_unread(message_id, mark_as_read):
    # Authenticate with Gmail API
    service = authenticate_gmail()

    # Modify the label of the specified email
    body = {'removeLabelIds': ['UNREAD']} if mark_as_read else {'addLabelIds': ['UNREAD']}
    service.users().messages().modify(userId='me', id=message_id, body=body).execute()

def move_message(message_id, destination_label):
    # Authenticate with Gmail API
    service = authenticate_gmail()

    # Get the current labels of the message
    message = service.users().messages().get(userId='me', id=message_id).execute()
    current_labels = message['labelIds']

    # Add the destination label
    current_labels.append(destination_label)

    # Modify the labels of the specified message
    body = {'addLabelIds': [destination_label]}
    service.users().messages().modify(userId='me', id=message_id, body=body).execute()

