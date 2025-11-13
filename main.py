import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import create_document, get_documents, db
from schemas import ContactMessage, ChatLog

app = FastAPI(title="MindForge Studio API", description="Backend for MindForge Studio website")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "MindForge Studio API is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from MindForge backend!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Public schemas endpoint for the viewer
@app.get("/schema")
async def get_schema_definitions():
    from schemas import User, Product, ContactMessage, ChatLog
    return {
        "user": User.model_json_schema(),
        "product": Product.model_json_schema(),
        "contactmessage": ContactMessage.model_json_schema(),
        "chatlog": ChatLog.model_json_schema(),
    }

# Contact form endpoint
@app.post("/api/contact")
async def submit_contact(message: ContactMessage):
    try:
        inserted_id = create_document("contactmessage", message)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simple chat log endpoint (stub for Test Zone)
class ChatRequest(BaseModel):
    bot: str
    prompt: str
    session_id: Optional[str] = None

@app.post("/api/chat")
async def chat(request: ChatRequest):
    # This is a placeholder echo bot; in a real setup you'd call your n8n or model API here
    response_text = f"[{request.bot}] Echo: " + request.prompt
    try:
        create_document("chatlog", ChatLog(bot=request.bot, prompt=request.prompt, response=response_text, session_id=request.session_id))
    except Exception:
        pass
    return {"bot": request.bot, "response": response_text}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
