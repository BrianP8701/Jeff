from server.data_loaders.gmail import read_emails, process_and_store_email
from server.data_loaders.files import process_files
from server.database.db import Database
from server.constants import folder_path
from sqlalchemy.exc import IntegrityError
from server.data_loaders.history import get_history, process_and_store_history

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
                    stored_emails = process_and_store_email(email)
                    for stored_email in stored_emails:
                        print(f"Stored email chunk: {stored_email['id']} - {stored_email['subject']}")
                except IntegrityError:
                    print(f"Email already exists: {email.subject}")
                    db.session.rollback()
                except Exception as e:
                    print(f"Error processing email: {e}")
                    db.session.rollback()

    print("Email ingestion complete.")

def ingest_files(folder_path: str):
    db = Database()
    try:
        process_files(folder_path)
    except Exception as e:
        print(f"Error during file ingestion: {e}")
        db.session.rollback()

def ingest_browser_history():
    try:
        print("Getting history")
        history_entries = get_history()
        print(history_entries)
        process_and_store_history(history_entries)
    except Exception as e:
        print(f"Error during history ingestion: {e}")
        db.session.rollback()

if __name__ == "__main__":
    db = Database()
    
    # Ingest emails
    ingest_recent_emails()
    
    # Ingest files
    ingest_files(folder_path)

    # Ingest browser history
    ingest_browser_history()
