from server.types.email import Email
from server.database.queries import create_email
from server.embeddings.embed import get_embedding

def process_and_store_email(email: Email):
    # Create embedding from email content
    content_to_embed = f"{email.subject}\n\n{email.body}"
    embedding = get_embedding(content_to_embed)

    # Prepare email data for database
    email_data = {
        "sender": email.sender,
        "subject": email.subject,
        "body": email.body,
        "message_id": email.message_id,
        "embedding": embedding
    }

    # Store email in database
    stored_email = create_email(email_data)
    return stored_email