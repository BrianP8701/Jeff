from fastapi import FastAPI
from pydantic import BaseModel
from server.data_loaders.gmail import open_gmail_message

app = FastAPI()

class EmailOpenRequest(BaseModel):
    message_id: str

@app.post("/open-email")
async def open_email(request: EmailOpenRequest):
    open_gmail_message(request.message_id)
    return {"status": "success", "message": "Email opened in browser"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
