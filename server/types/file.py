from pydantic import BaseModel

class File(BaseModel):
    id: str
    name: str
    path: str
    content: str
