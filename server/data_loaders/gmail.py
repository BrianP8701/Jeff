import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
import webbrowser

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

def read_emails(days: int) -> List[Dict[str, List[Email]]]:
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    email_threads = []
    
    try:
        date_days_ago = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
        query = f"after:{date_days_ago}"
        results = service.users().threads().list(userId='me', labelIds=['INBOX'], q=query).execute()
        threads = results.get('threads', [])
        
        if not threads:
            print(f'No threads in the last {days} days.')
            return email_threads
        
        for thread in threads:
            thread_id = thread['id']
            thread_data = service.users().threads().get(userId='me', id=thread_id).execute()
            messages = thread_data['messages']
            
            thread_emails = []
            for message in messages:
                # Extract sender, subject, and body as before
                headers = message['payload']['headers']
                sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown')
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
                
                if 'parts' in message['payload']:
                    parts = message['payload']['parts']
                    data = next((part['body']['data'] for part in parts if part['mimeType'] == 'text/plain'), None)
                else:
                    data = message['payload']['body'].get('data')
                
                body = base64.urlsafe_b64decode(data).decode('utf-8') if data else ''
                
                thread_emails.append(Email(
                    sender=sender,
                    subject=subject,
                    body=body,
                    message_id=message['id']
                ))
            
            email_threads.append({thread_id: thread_emails})
    
    except Exception as error:
        print(f'An error occurred: {error}')
    
    return email_threads

def open_gmail_message(message_id: str):
    base_url = "https://mail.google.com/mail/u/0/?tab=rm&ogbl#inbox/"
    full_url = f"{base_url}{message_id}"
    webbrowser.open(full_url)

if __name__ == "__main__":
    days = 1
    recent_email_threads = read_emails(days)
    for thread in recent_email_threads:
        for thread_id, emails in thread.items():
            print(f"Thread ID: {thread_id}")
            for i, email in enumerate(emails, 1):
                print(f"  Message {i}:")
                print(f"    From: {email.sender}")
                print(f"    Subject: {email.subject}")
                print(f"    Body: {email.body[:100]}...")
                print(f"    Message ID: {email.message_id}")
                
                # Add this line to open the email in the browser
                open_gmail_message(email.message_id)
            
            print("---")
