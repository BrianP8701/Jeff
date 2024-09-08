from dotenv import load_dotenv
from typing import List, Dict
from server.types.email import Email
from server.database.queries import create_email
from server.embeddings.embed import get_embedding, chunk_content

load_dotenv()

def process_and_store_email(email: Email) -> List[Dict]:
    stored_emails = []
    chunks = chunk_content(email.body)
    
    for i, chunk in enumerate(chunks):
        # Include subject and sender in the content to embed
        content_to_embed = f"Subject: {email.subject}\nFrom: {email.sender}\n\n{chunk}"
        embedding = get_embedding("Email subject: " + email.subject + "sender: " + email.sender + "content: " + content_to_embed)

        # Prepare email data for database
        email_data = {
            "sender": email.sender,
            "subject": f"{email.subject} (chunk {i+1}/{len(chunks)})",
            "body": chunk,
            "message_id": f"{email.message_id}",
            "embedding": embedding
        }

        # Store email in database
        stored_email = create_email(email_data)
        stored_emails.append({"id": stored_email[0], "subject": email_data["subject"]})
    
    return stored_emails
