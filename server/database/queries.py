from .db import Database

db = Database()

# Email CRUD operations
def create_email(email: dict):
    if 'embedding_id' in email:
        del email['embedding_id']
    return db.create('emails', email)

def read_email(email_id: int):
    return db.read('emails', email_id)

def update_email(email_id: int, email: dict):
    return db.update('emails', email_id, email)

def delete_email(email_id: int):
    return db.delete('emails', email_id)

# File CRUD operations
def create_file(file: dict):
    if 'embedding_id' in file:
        del file['embedding_id']
    return db.create('files', file)

def read_file(file_id: int):
    return db.read('files', file_id)

def update_file(file_id: int, file: dict):
    return db.update('files', file_id, file)

def delete_file(file_id: int):
    return db.delete('files', file_id)

# Link CRUD operations
def create_link(link: dict):
    if 'embedding_id' in link:
        del link['embedding_id']
    return db.create('links', link)

def read_link(link_id: int):
    return db.read('links', link_id)

def update_link(link_id: int, link: dict):
    return db.update('links', link_id, link)

def delete_link(link_id: int):
    return db.delete('links', link_id)
