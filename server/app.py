#    uvicorn server.app:app --host 0.0.0.0 --port 8000
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from pydantic import BaseModel
from .data_loaders.gmail import open_gmail_message
from .apis.exa_client import get_contents_for_url
from enum import Enum
from typing import List
import logging

# Add this near the top of the file, after imports
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ItemType(str, Enum):
    FILE = "FILE"
    URL = "URL"

class SearchItem(BaseModel):
    type: ItemType
    value: str

class SearchResponse(BaseModel):
    items: List[SearchItem]

class EmailOpenRequest(BaseModel):
    message_id: str

class SearchContentsRequest(BaseModel):
    url: str

app = FastAPI()

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Server is running"}

@app.post("/open-email")
async def open_email(request: EmailOpenRequest):
    open_gmail_message(request.message_id)
    return {"status": "success", "message": "Email opened in browser"}

@app.post("/search-contents")
async def search_contents(request: SearchContentsRequest):
    print(request.url)
    result = get_contents_for_url(request.url)
    return {"status": "success", "message": result}

@app.get("/search")
async def search():
    logger.info("Search endpoint accessed")
    # This is a mock response. In a real scenario, you'd implement actual search logic here.
    return SearchResponse(items=[
        SearchItem(type=ItemType.FILE, value="/path/to/file1.txt"),
        SearchItem(type=ItemType.FILE, value="/path/to/file2.pdf"),
        SearchItem(type=ItemType.URL, value="https://www.example.com"),
        SearchItem(type=ItemType.URL, value="https://www.google.com")
    ])

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
