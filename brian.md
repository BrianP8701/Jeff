

# Storage/database
we want a simple storage solution.

we need to store:
- emails
class Email(BaseModel):
    sender: str
    subject: str
    body: str
    message_id: str
    embedding_id: str
- files
class File(BaseModel):
    name: str
    path: str
    content: str
    embedding_id: str
- links
class Link(BaseModel):
    url: str
    title: str
    content: str
    embedding_id: str

and we want a vector database for each of these and each of the objects needs a corresponding vector embedding.

for this project we can sqlite