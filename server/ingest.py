from server.data_loaders.gmail import read_emails, process_and_store_email
from server.database.db import Database

def ingest_recent_emails(days: int = 7):
    # Initialize the database
    db = Database()

    # Get recent email threads
    recent_email_threads = read_emails(days)

    # Process each email in each thread
    for thread in recent_email_threads:
        for thread_id, emails in thread.items():
            for email in emails:
                try:
                    stored_email = process_and_store_email(email)
                    print(f"Stored email: {stored_email.id} - {stored_email.subject}")
                except Exception as e:
                    print(f"Error processing email: {e}")

    print("Email ingestion complete.")

if __name__ == "__main__":
    ingest_recent_emails()
x