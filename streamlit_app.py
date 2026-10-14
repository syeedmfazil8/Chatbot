import streamlit as st
from groq import Groq

st.set_page_config(page_title="My Chatbot", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    .main { background-color: #f7f8fa; }
    .stChatMessage { border-radius: 12px; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 MUHAMMAD FAZIL'S CHATBOT")
st.caption("Powered by Groq + Llama")

client = Groq(api_key="PASTE_YOUR_NEW_GROQ_KEY_HERE")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a friendly, helpful chatbot. Keep replies short and casual."}
    ]

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=st.session_state.messages
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})