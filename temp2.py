import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

class Email(BaseModel):
    sender: str
    subject: str
    body: str
    message_id: str

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                os.remove('token.json')
                return get_credentials()
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def read_emails(days: int) -> List[Email]:
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    emails = []
    
    try:
        # Calculate the date 'days' ago
        date_days_ago = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
        
        # Modify the query to get emails after the specified date
        query = f"after:{date_days_ago}"
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q=query).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print(f'No messages in the last {days} days.')
            return emails
        
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            
            # Extract sender and subject
            headers = msg['payload']['headers']
            sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown')
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
            
            # Extract and decode message body
            if 'parts' in msg['payload']:
                parts = msg['payload']['parts']
                data = next((part['body']['data'] for part in parts if part['mimeType'] == 'text/plain'), None)
            else:
                data = msg['payload']['body'].get('data')
            
            body = base64.urlsafe_b64decode(data).decode('utf-8') if data else ''
            
            emails.append(Email(
                sender=sender,
                subject=subject,
                body=body,
                message_id=message['id']
            ))
    
    except Exception as error:
        print(f'An error occurred: {error}')
    
    return emails

if __name__ == "__main__":
    days = 1
    recent_emails = read_emails(days)
    for email in recent_emails:
        print(f"From: {email.sender}")
        print(f"Subject: {email.subject}")
        print(f"Body: {email.body[:100]}...")  # Print first 100 characters of the body
        print(f"Message ID: {email.message_id}")
        print("---")
