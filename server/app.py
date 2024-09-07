from fastapi import FastAPI
from pydantic import BaseModel
from data_loaders.gmail import open_gmail_message
from apis.exa_client import get_contents_for_url

app = FastAPI()

class EmailOpenRequest(BaseModel):
    message_id: str

class SearchContentsRequest(BaseModel):
    url: str

@app.post("/open-email")
async def open_email(request: EmailOpenRequest):
    open_gmail_message(request.message_id)
    return {"status": "success", "message": "Email opened in browser"}

@app.post("/search-contents")
async def search_contents(request: SearchContentsRequest):
    print(request.url)
    result = get_contents_for_url(request.url)
    return {"status": "success", "message": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
