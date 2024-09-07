# Script to get the refresh token, client id, and client secret
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret_911903497338-n4ldjblb3b9t51dr5f51ojtif73919ks.apps.googleusercontent.com.json',  # Replace with the path to your downloaded client config
    scopes=SCOPES
)

credentials = flow.run_local_server(port=0)

print(f"Your refresh token: {credentials.refresh_token}")
print(f"Your client id: {credentials.client_id}")
print(f"Your client secret: {credentials.client_secret}")
