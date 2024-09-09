from .db import Database
from .tables import Email, File, Link, Embedding, ContentType

db = Database()

# Email CRUD operations
def create_email(email: dict):
    embedding = email.pop('embedding', None)
    email_obj = db.create('emails', email)
    
    if embedding:
        embedding_data = {
            'embedding': embedding,
            'content_type': ContentType.EMAIL,
            'email_id': email_obj.id
        }
        db.create('embeddings', embedding_data)
    
    return email_obj, embedding

def read_email(email_id: int):
    email = db.read('emails', email_id)
    embedding_obj = db.session.query(Embedding).filter_by(email_id=email_id).first()
    embedding = embedding_obj.embedding if embedding_obj else None
    return email, embedding

def update_email(email_id: int, email: dict):
    updated_email = db.update('emails', email_id, email)
    embedding_obj = db.session.query(Embedding).filter_by(email_id=email_id).first()
    embedding = embedding_obj.embedding if embedding_obj else None
    return updated_email, embedding

def delete_email(email_id: int):
    db.session.query(Embedding).filter_by(email_id=email_id).delete()
    deleted_email = db.delete('emails', email_id)
    return deleted_email

# File CRUD operations
def create_file(file: dict):
    embedding = file.pop('embedding', None)
    file_obj = db.create('files', file)
    
    if embedding:
        embedding_data = {
            'embedding': embedding,
            'content_type': ContentType.FILE,
            'file_id': file_obj.id
        }
        db.create('embeddings', embedding_data)
    
    return file_obj

def read_file(file_id: int):
    return db.read('files', file_id)

def update_file(file_id: int, file: dict):
    return db.update('files', file_id, file)

def delete_file(file_id: int):
    return db.delete('files', file_id)

# Link CRUD operations
def create_link(link: dict):
    embedding = link.pop('embedding', None)
    link_obj = db.create('links', link)
    
    if embedding:
        embedding_data = {
            'embedding': embedding,
            'content_type': ContentType.LINK,
            'link_id': link_obj.id
        }
        db.create('embeddings', embedding_data)
    
    return link_obj

def read_link(link_id: int):
    return db.read('links', link_id)

def update_link(link_id: int, link: dict):
    return db.update('links', link_id, link)

def delete_link(link_id: int):
    return db.delete('links', link_id)

def get_file_by_path_and_content(file_path: str, content: str):
    return db.session.query(File).filter_by(path=file_path, content=content).first()

def get_file_by_content_hash(content_hash: str):
    return db.session.query(File).filter_by(content_hash=content_hash).first()

def get_link_by_url(url: str):
    return db.session.query(Link).filter_by(url=url).first()
