from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
import pickle

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_emails(days: int):
    creds = Credentials.from_authorized_user_info(info={
        "client_id": os.getenv("GMAIL_CLIENT_ID"),
        "client_secret": os.getenv("GMAIL_CLIENT_SECRET"),
        "refresh_token": os.getenv("GMAIL_REFRESH_TOKEN")
    }, scopes=SCOPES)

    service = build('gmail', 'v1', credentials=creds)

    # Calculate the date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    # Format dates for the query
    query = f'after:{start_date.strftime("%Y/%m/%d")} before:{end_date.strftime("%Y/%m/%d")}'

    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    emails = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        emails.append(msg)

    return emails

def get_gmail_service():
    creds = None
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            # Token refresh failed, re-run the authorization flow
            flow = InstalledAppFlow.from_client_secrets_file('path/to/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('path/to/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    
    # Save the new credentials
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

# Example usage
emails = get_gmail_emails(7)  # Get emails from the last 7 days
print(f"Found {len(emails)} emails")

