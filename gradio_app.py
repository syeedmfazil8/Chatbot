import gradio as gr
from groq import Groq

client = Groq(api_key="PASTE_YOUR_NEW_GROQ_KEY_HERE")
SYSTEM_PROMPT = "You are a friendly, helpful chatbot. Keep replies short and casual."

def chat(message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for user_msg, bot_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages
    )
    return response.choices[0].message.content

demo = gr.ChatInterface(
    fn=chat,
    title="🤖 MUHAMMAD FAZIL'CHATBOT",
    description="Powered by Groq + Llama",
    examples=["Hello!", "Tell me a joke", "What is Python?"],
    theme="soft"
)

demo.launch()