#    uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends
from fastapi.routing import APIRoute
from pydantic import BaseModel
from .data_loaders.gmail import open_gmail_message
from .apis.exa_client import get_contents_for_url
from enum import Enum
from typing import List, Optional
import logging
from server.database.db import Database
from server.database.tables import ContentType
from server.apis.openai_client import generate_answer_summary

# Add this near the top of the file, after imports
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name

class ItemType(str, Enum):
    FILE = "FILE"
    URL = "URL"

class EmailOpenRequest(BaseModel):
    message_id: str

class SearchContentsRequest(BaseModel):
    url: str

class SearchResult(BaseModel):
    type: ItemType
    source: str
    title: str
    distance: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    answer_summary: Optional[str] = None

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

@app.get("/search", response_model=SearchResponse)
@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    logger.info(f"Search endpoint accessed with query: {request.query}")
    
    db = Database()
    results = db.similarity_search(request.query, request.limit)
    
    summary_context_string = ""
    search_results = []
    print("\n\nresults: " + str(results) + "\n\n")
    for result in results:
        item_type = ItemType.FILE if result['content_type'] == ContentType.FILE else ItemType.URL
        source = result['source']
        summary_context_string += "\n\n" + result['content']
        title = result.get('title', '')
        
        if result['content_type'] == ContentType.EMAIL:
            source = f"https://mail.google.com/mail/u/0/#search/rfc822msgid:{source}"
        
        search_results.append(SearchResult(
            type=item_type,
            source=source,
            title=title,
            distance=result['distance']
        ))
    
    answer_summary = generate_answer_summary(request.query, summary_context_string)
    
    logger.info(f"Search results: {search_results}")
    return SearchResponse(results=search_results, answer_summary=answer_summary)

# Add this at the end of the file
use_route_names_as_operation_ids(app)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
