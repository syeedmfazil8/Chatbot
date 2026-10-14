from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from groq import Groq
from typing import List

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

client = Groq(api_key="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")
SYSTEM_PROMPT = "You are a friendly, helpful chatbot. Keep replies short and casual."

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(req: ChatRequest):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [m.dict() for m in req.messages]

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages
    )
    reply = response.choices[0].message.content
    return JSONResponse({"reply": reply})