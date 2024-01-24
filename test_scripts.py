# Test Scripts to generate data that can be stored in local database
# Authenticate to Google’s Gmail API using OAuth fetch a list of emails from your Inbox. Do NOT use IMAP.

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime
import re
import random
from datetime import datetime, timedelta

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

def get_random_message_ids(max_messages=10):
    # Authenticate with Gmail API
    service = authenticate_gmail()

    # Get a list of all messages
    results = service.users().messages().list(userId='me').execute()
    messages = results.get('messages', [])

    # Get a random sample of message IDs
    random_message_ids = random.sample([message['id'] for message in messages], min(max_messages, len(messages)))

    return random_message_ids

def list_labels():
    # Authenticate with Gmail API
    service = authenticate_gmail()

    # Get a list of all labels
    labels = service.users().labels().list(userId='me').execute().get('labels', [])

    return labels

def parse_date(date_string):
    # Define a list of possible date formats
    date_formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%a, %d %b %Y %H:%M:%S"
        # Add more formats as needed
    ]

    # Attempt to parse the date using each format
    for format_str in date_formats:
        try:
            parsed_datetime = datetime.strptime(date_string, format_str)
            return parsed_datetime
        except ValueError:
            pass

    # If none of the formats match, handle it gracefully (returning None in this case)
    return None

def get_message_headers(message_id):
    # Authenticate with Gmail API
    service = authenticate_gmail()

    # Get the details of the specified message
    message = service.users().messages().get(userId='me', id=message_id).execute()

    # Initialize variables to store email details
    sender = None
    to = None
    subject = None

    # Extract details from headers
    headers = message['payload']['headers']
    for header in headers:
        if header['name'] == 'From':
            sender = header['value']
            # Use regular expression to extract the email address
            match = re.search(r'<([^>]+)>', sender)
            if match:
                parsed_sender = match.group(1)

            else:
                print(f'No match for mail {sender}')
                parsed_sender = sender            
        elif header['name'] == 'To':
            to = header['value']
        elif header['name'] == 'Subject':
            subject =  header['value'].replace("'", " ")
        elif header['name'] == 'Date':
            if 'UTC' in header['value']:
                date_string =  header['value']
                date_string = date_string.split('(')[0].strip()
                parsed_datetime = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")
            else:
                parsed_datetime = parse_date(header['value'])

    return {
        'From': parsed_sender,
        'To': to,
        'Subject': subject,
        'Date Received': parsed_datetime
    }

if __name__ == '__main__':
    max_messages = 10
    
    # Get the message ID based on the query
    random_message_ids = get_random_message_ids(max_messages)
    for message_id in random_message_ids:
        email_details = get_message_headers(message_id)
        print(f"INSERT INTO assignment.mail VALUES ('{message_id}', '{email_details['From']}', '{email_details['To']}', '{email_details['Subject']}', '{email_details['Date Received']}');")
        
    # Get the list of existing labels
    # existing_labels = list_labels()

    # if existing_labels:
    #     print('Existing Labels:')
    #     for label in existing_labels:
    #         print(label['name'])
    # else:
    #     print('No labels found.')

    # if message_id:
    #     # Get sender and subject details
    #     sender, subject = get_message_details(message_id)


    # else:
    #     print('Unable to retrieve message ID.')



