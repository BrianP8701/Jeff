from pydantic import BaseModel

class Email(BaseModel):
    sender: str
    subject: str
    body: str
    message_id: str