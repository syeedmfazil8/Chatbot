from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from groq import Groq
from typing import List
import os

app = FastAPI()

# 🔐 Better: read from environment variable, fall back to hardcoded for local dev
API_KEY = os.getenv("GROQ_API_KEY", "type you API Key")
client = Groq(api_key=API_KEY)

SYSTEM_PROMPT = (
    "You are Fazil's AI assistant — smart, friendly, and concise. "
    "Use markdown for formatting when helpful (bold, bullet lists, code blocks). "
    "Keep casual replies short; give detail when the user asks for it."
)

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fazil AI — Assistant</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<style>
  :root {
    --bg: #0b0f1a;
    --panel: #111827;
    --text: #e5e7eb;
    --muted: #94a3b8;
    --accent: #6366f1;
    --accent-2: #8b5cf6;
    --user-bubble: linear-gradient(135deg, #6366f1, #8b5cf6);
    --bot-bubble: #1e293b;
    --border: rgba(255,255,255,0.08);
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  html, body {
    height: 100%;
    font-family: 'Inter', -apple-system, "Segoe UI", Roboto, sans-serif;
    background: radial-gradient(circle at 20% 0%, #1e1b4b 0%, #0b0f1a 45%, #05070d 100%);
    color: var(--text);
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
  }

  .chat-container {
    width: 100%;
    max-width: 700px;
    height: 92vh;
    background: rgba(17, 24, 39, 0.85);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 24px;
    box-shadow: 0 30px 80px rgba(0,0,0,0.55), 0 0 0 1px rgba(255,255,255,0.03) inset;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: rise 0.5s cubic-bezier(.2,.8,.2,1);
  }

  @keyframes rise {
    from { opacity: 0; transform: translateY(20px) scale(0.98); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }

  /* Header */
  .chat-header {
    display: flex; align-items: center; gap: 14px;
    padding: 18px 22px;
    background: linear-gradient(135deg, rgba(99,102,241,0.18), rgba(139,92,246,0.12));
    border-bottom: 1px solid var(--border);
    position: relative;
  }
  .chat-header::after {
    content: ""; position: absolute; left: 0; right: 0; bottom: -1px; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0.6;
  }
  .avatar-wrap { position: relative; }
  .avatar {
    width: 46px; height: 46px; border-radius: 14px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    display: flex; align-items: center; justify-content: center;
    font-size: 24px;
    box-shadow: 0 6px 20px rgba(99,102,241,0.45);
  }
  .online-dot {
    position: absolute; bottom: -2px; right: -2px;
    width: 14px; height: 14px; border-radius: 50%;
    background: #22c55e; border: 3px solid var(--panel);
    box-shadow: 0 0 10px #22c55e;
    animation: pulse 2s infinite;
  }
  @keyframes pulse {
    0%,100% { box-shadow: 0 0 8px #22c55e; }
    50%     { box-shadow: 0 0 16px #22c55e, 0 0 24px rgba(34,197,94,0.5); }
  }
  .header-text h1 {
    font-size: 16px; font-weight: 700; letter-spacing: 0.3px;
    background: linear-gradient(135deg, #fff, #c7d2fe);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .header-text .status {
    font-size: 12px; color: #4ade80;
    display: flex; align-items: center; gap: 5px; margin-top: 2px;
  }
  .header-text .status::before {
    content: ""; width: 6px; height: 6px; border-radius: 50%;
    background: #22c55e; box-shadow: 0 0 8px #22c55e;
  }
  .new-chat-btn {
    margin-left: auto;
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 8px 14px; border-radius: 10px;
    font-size: 12px; font-weight: 600;
    cursor: pointer; transition: all 0.2s;
  }
  .new-chat-btn:hover {
    background: rgba(99,102,241,0.2);
    border-color: rgba(99,102,241,0.5);
  }

  /* Chat area */
  .chat-box {
    flex: 1; overflow-y: auto;
    padding: 24px 20px;
    display: flex; flex-direction: column; gap: 18px;
    scroll-behavior: smooth;
  }
  .chat-box::-webkit-scrollbar { width: 8px; }
  .chat-box::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.08); border-radius: 10px;
  }
  .chat-box::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }

  /* Messages */
  .message {
    display: flex; gap: 10px; align-items: flex-end;
    animation: msgIn 0.35s cubic-bezier(.2,.8,.2,1);
  }
  @keyframes msgIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .message.user { flex-direction: row-reverse; }
  .message.bot  { flex-direction: row; }

  .msg-avatar {
    width: 34px; height: 34px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
  }
  .message.bot .msg-avatar {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    box-shadow: 0 4px 14px rgba(99,102,241,0.4);
  }
  .message.user .msg-avatar {
    background: linear-gradient(135deg, #0ea5e9, #06b6d4);
    box-shadow: 0 4px 14px rgba(14,165,233,0.4);
  }

  .bubble {
    max-width: 72%;
    padding: 12px 16px;
    border-radius: 18px;
    font-size: 14.5px;
    line-height: 1.6;
    word-wrap: break-word;
    position: relative;
    animation: bubbleIn 0.3s ease;
  }
  @keyframes bubbleIn {
    from { transform: scale(0.94); opacity: 0; }
    to   { transform: scale(1);    opacity: 1; }
  }

  .message.bot .bubble {
    background: var(--bot-bubble);
    color: var(--text);
    border: 1px solid var(--border);
    border-bottom-left-radius: 6px;
  }
  .message.user .bubble {
    background: var(--user-bubble);
    color: #fff;
    border-bottom-right-radius: 6px;
    box-shadow: 0 6px 20px rgba(99,102,241,0.35);
  }

  /* Markdown inside bot bubbles */
  .bubble p { margin-bottom: 8px; }
  .bubble p:last-child { margin-bottom: 0; }
  .bubble ul, .bubble ol { margin: 8px 0 8px 20px; }
  .bubble li { margin-bottom: 4px; }
  .bubble strong { color: #c7d2fe; }
  .bubble code {
    background: rgba(0,0,0,0.35);
    padding: 2px 6px; border-radius: 6px;
    font-family: 'Fira Code', Consolas, monospace;
    font-size: 13px;
  }
  .bubble pre {
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.06);
    padding: 12px 14px; border-radius: 12px;
    overflow-x: auto;
    margin: 10px 0;
    font-size: 13px;
  }
  .bubble pre code { background: none; padding: 0; }
  .bubble a { color: #a5b4fc; }
  .bubble blockquote {
    border-left: 3px solid var(--accent);
    padding-left: 12px; margin: 8px 0;
    color: var(--muted);
  }

  /* Copy button */
  .copy-btn {
    position: absolute;
    top: 8px; right: 8px;
    background: rgba(255,255,255,0.06);
    border: 1px solid var(--border);
    color: var(--muted);
    padding: 3px 8px;
    font-size: 10.5px;
    border-radius: 6px;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.2s, background 0.2s;
  }
  .message.bot .bubble:hover .copy-btn { opacity: 1; }
  .copy-btn:hover { background: rgba(99,102,241,0.25); color: #fff; }

  .time {
    display: block; font-size: 10.5px;
    color: var(--muted); margin-top: 6px;
    text-align: right; opacity: 0.75;
  }
  .message.user .time { color: rgba(255,255,255,0.7); }

  /* Typing dots */
  .typing .bubble {
    display: flex; gap: 5px;
    padding: 14px 18px; align-items: center;
  }
  .dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #94a3b8;
    animation: bounce 1.4s infinite ease-in-out both;
  }
  .dot:nth-child(1) { animation-delay: -0.32s; }
  .dot:nth-child(2) { animation-delay: -0.16s; }
  @keyframes bounce {
    0%,80%,100% { transform: scale(0.6); opacity: 0.4; }
    40%         { transform: scale(1);   opacity: 1; }
  }

  /* Input */
  .chat-input {
    display: flex; padding: 16px 18px; gap: 10px;
    background: rgba(15, 23, 42, 0.7);
    border-top: 1px solid var(--border);
    align-items: center;
  }
  .input-wrap { flex: 1; }
  .chat-input input {
    width: 100%;
    padding: 14px 18px;
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: 14px;
    color: var(--text);
    font-size: 14.5px;
    outline: none;
    transition: all 0.2s;
  }
  .chat-input input::placeholder { color: var(--muted); }
  .chat-input input:focus {
    border-color: rgba(99,102,241,0.6);
    background: rgba(99,102,241,0.06);
    box-shadow: 0 0 0 4px rgba(99,102,241,0.12);
  }
  .chat-input button {
    width: 50px; height: 50px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #fff; border: none; border-radius: 14px;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.2s;
    box-shadow: 0 6px 18px rgba(99,102,241,0.45);
  }
  .chat-input button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(99,102,241,0.6);
  }
  .chat-input button:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none; }
  .chat-input button svg { width: 20px; height: 20px; }

  @media (max-width: 640px) {
    .chat-container { height: 100vh; border-radius: 0; max-width: 100%; }
    .bubble { max-width: 82%; }
  }
</style>
</head>
<body>
<div class="chat-container">

  <header class="chat-header">
    <div class="avatar-wrap">
      <div class="avatar">🤖</div>
      <span class="online-dot"></span>
    </div>
    <div class="header-text">
      <h1>MUHAMMAD FAZIL'S AI</h1>
      <span class="status">Online</span>
    </div>
    <button class="new-chat-btn" id="new-chat-btn">+ New Chat</button>
  </header>

  <main id="chat-box" class="chat-box">
    <div class="message bot">
      <div class="msg-avatar">🤖</div>
      <div>
        <div class="bubble">Hi! I'm Fazil's AI assistant. How can I help you today? ✨</div>
        <span class="time" id="first-time"></span>
      </div>
    </div>
  </main>

  <footer class="chat-input">
    <div class="input-wrap">
      <input id="user-input" type="text" placeholder="Type your message..." autocomplete="off"/>
    </div>
    <button id="send-btn" title="Send">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
      </svg>
    </button>
  </footer>

</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.0/marked.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script>
const chatBox   = document.getElementById("chat-box");
const input     = document.getElementById("user-input");
const sendBtn   = document.getElementById("send-btn");
const newChatBtn= document.getElementById("new-chat-btn");
const firstTime = document.getElementById("first-time");

let history = [];

function now() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
if (firstTime) firstTime.textContent = now();

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

function renderMarkdown(text) {
  // For user messages: escape everything (safety)
  // For bot messages: render markdown
  marked.setOptions({ breaks: true, gfm: true });
  return marked.parse(text);
}

function addMessage(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `message ${role}`;

  const av = document.createElement("div");
  av.className = "msg-avatar";
  av.textContent = role === "user" ? "👤" : "🤖";

  const content = document.createElement("div");
  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (role === "bot") {
    bubble.innerHTML = renderMarkdown(text);
    // Copy button
    const copy = document.createElement("button");
    copy.className = "copy-btn";
    copy.textContent = "Copy";
    copy.onclick = () => {
      navigator.clipboard.writeText(text);
      copy.textContent = "Copied!";
      setTimeout(() => copy.textContent = "Copy", 1200);
    };
    bubble.appendChild(copy);
    // Highlight code blocks
    bubble.querySelectorAll("pre code").forEach(el => hljs.highlightElement(el));
  } else {
    bubble.textContent = text;
  }

  const time = document.createElement("span");
  time.className = "time";
  time.textContent = now();

  content.appendChild(bubble);
  content.appendChild(time);
  wrap.appendChild(av);
  wrap.appendChild(content);

  chatBox.appendChild(wrap);
  chatBox.scrollTop = chatBox.scrollHeight;
  return wrap;
}

function addTyping() {
  const wrap = document.createElement("div");
  wrap.className = "message bot typing";
  wrap.innerHTML = `
    <div class="msg-avatar">🤖</div>
    <div>
      <div class="bubble">
        <span class="dot"></span><span class="dot"></span><span class="dot"></span>
      </div>
    </div>`;
  chatBox.appendChild(wrap);
  chatBox.scrollTop = chatBox.scrollHeight;
  return wrap;
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  input.value = "";
  sendBtn.disabled = true;

  addMessage("user", text);
  history.push({ role: "user", content: text });

  const typing = addTyping();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    typing.remove();
    addMessage("bot", data.reply);
    history.push({ role: "assistant", content: data.reply });
  } catch (err) {
    typing.remove();
    addMessage("bot", "⚠️ **Error:** could not reach server. Please try again.");
    console.error(err);
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

newChatBtn.addEventListener("click", () => {
  if (history.length && !confirm("Start a new chat? Current conversation will be cleared.")) return;
  history = [];
  chatBox.innerHTML = `
    <div class="message bot">
      <div class="msg-avatar">🤖</div>
      <div>
        <div class="bubble">New chat started! What would you like to talk about? ✨</div>
        <span class="time">${now()}</span>
      </div>
    </div>`;
});
</script>
</body>
</html>
"""

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=HTML_PAGE)

@app.post("/chat")
async def chat(req: ChatRequest):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [m.dict() for m in req.messages]

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"⚠️ Server error: `{str(e)}`"
    return JSONResponse({"reply": reply})