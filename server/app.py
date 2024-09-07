#    uvicorn server.app:app --host 0.0.0.0 --port 8000
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from pydantic import BaseModel
from .data_loaders.gmail import open_gmail_message
from .apis.exa_client import get_contents_for_url
from enum import Enum
from typing import List, Optional
import logging
from server.database.db import Database
from server.database.tables import ContentType

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

class SearchResult(BaseModel):
    type: ItemType
    value: str
    distance: float

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

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

@app.post("/search", response_model=List[SearchResult])
async def search(request: SearchRequest):
    logger.info(f"Search endpoint accessed with query: {request.query}")
    
    db = Database()
    results = db.similarity_search(request.query, request.limit)
    
    search_results = []
    for result in results:
        item_type = ItemType.FILE if result.content_type == ContentType.FILE else ItemType.URL
        value = result.content_identifier
        
        if result.content_type == ContentType.EMAIL:
            value = f"https://mail.google.com/mail/u/0/#search/rfc822msgid:{value}"
        
        search_results.append(SearchResult(
            type=item_type,
            value=value,
            distance=result.distance
        ))
    
    return search_results

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
