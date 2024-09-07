from server.database.queries import (
    create_email, read_email, update_email, delete_email,
    create_file, read_file, update_file, delete_file,
    create_link, read_link, update_link, delete_link
)
from server.database.db import Database
def test_email_crud():
    print("Testing Email CRUD operations:")
    # Create
    email_data = {
        "sender": "test@example.com",
        "subject": "Test Email",
        "body": "This is a test email body.",
        "message_id": "test123",
        "embedding_id": "emb123"
    }
    email = create_email(email_data)
    print(f"Created email: {email.id}")

    # Read
    read_email_obj = read_email(email.id)
    print(f"Read email: {read_email_obj.subject}")

    # Update
    update_data = {"subject": "Updated Test Email"}
    updated_email = update_email(email.id, update_data)
    print(f"Updated email subject: {updated_email.subject}")

    # Delete
    deleted_email = delete_email(email.id)
    print(f"Deleted email: {deleted_email.id}")

def test_file_crud():
    print("\nTesting File CRUD operations:")
    # Create
    file_data = {
        "name": "test.txt",
        "path": "/path/to/test.txt",
        "content": "This is a test file content.",
        "embedding_id": "emb456"
    }
    file = create_file(file_data)
    print(f"Created file: {file.id}")

    # Read
    read_file_obj = read_file(file.id)
    print(f"Read file: {read_file_obj.name}")

    # Update
    update_data = {"content": "Updated test file content."}
    updated_file = update_file(file.id, update_data)
    print(f"Updated file content: {updated_file.content}")

    # Delete
    deleted_file = delete_file(file.id)
    print(f"Deleted file: {deleted_file.id}")

def test_link_crud():
    print("\nTesting Link CRUD operations:")
    # Create
    link_data = {
        "url": "https://example.com",
        "title": "Example Website",
        "content": "This is an example website content.",
        "embedding_id": "emb789"
    }
    link = create_link(link_data)
    print(f"Created link: {link.id}")

    # Read
    read_link_obj = read_link(link.id)
    print(f"Read link: {read_link_obj.title}")

    # Update
    update_data = {"title": "Updated Example Website"}
    updated_link = update_link(link.id, update_data)
    print(f"Updated link title: {updated_link.title}")

    # Delete
    deleted_link = delete_link(link.id)
    print(f"Deleted link: {deleted_link.id}")

if __name__ == "__main__":
    db = Database()
    db.clear_all_tables()
    test_email_crud()
    test_file_crud()
    test_link_crud()