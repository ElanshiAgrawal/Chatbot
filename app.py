import streamlit as st
from groq import Groq
import uuid

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Groq Chatbox", page_icon="⚡", layout="wide")

st.title("⚡ Groq Chatbox")
st.caption("ChatGPT-style chatbot with Groq API")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("💬 Chats")

    # Initialize session
    if "sessions" not in st.session_state:
        st.session_state.sessions = {}
    if "current_chat" not in st.session_state:
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {"title": "New Chat", "messages": []}
        st.session_state.current_chat = new_id

    # New Chat
    if st.button("➕ New Chat"):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {"title": "New Chat", "messages": []}
        st.session_state.current_chat = new_id
        st.rerun()

    st.divider()

    # Show chats
    for chat_id, chat in st.session_state.sessions.items():
        if st.button(
            chat["title"],
            key=chat_id,
            use_container_width=True,
            type="primary" if chat_id == st.session_state.current_chat else "secondary"
        ):
            st.session_state.current_chat = chat_id
            st.rerun()

    st.divider()

    # Rename chat
    st.subheader("✏ Rename Chat")
    new_name = st.text_input("Enter new name")

    if st.button("Save Name"):
        st.session_state.sessions[st.session_state.current_chat]["title"] = new_name
        st.rerun()

    st.divider()

    # Delete chat
    if st.button("🗑 Delete Chat"):
        del st.session_state.sessions[st.session_state.current_chat]

        if st.session_state.sessions:
            st.session_state.current_chat = list(st.session_state.sessions.keys())[0]
        else:
            new_id = str(uuid.uuid4())
            st.session_state.sessions[new_id] = {"title": "New Chat", "messages": []}
            st.session_state.current_chat = new_id

        st.rerun()

    st.divider()

    # Setup
    st.subheader("⚙ Setup")

    api_key = st.secrets["GROQ_API_KEY"]

    model = st.selectbox(
        "Model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ]
    )

# ---------------- CHAT AREA ----------------
messages = st.session_state.sessions[st.session_state.current_chat]["messages"]

# Show messages
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
user_input = st.chat_input("Type a message...")

if user_input:

    if not api_key:
        st.error("⚠️ Enter API key in sidebar")
        st.stop()

    # Save user message
    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Auto title (first message)
    if len(messages) == 1:
        st.session_state.sessions[st.session_state.current_chat]["title"] = user_input[:30]

    # Call API
    client = Groq(api_key=api_key)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""

        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "You are a helpful assistant."}, *messages],
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_reply += chunk.choices[0].delta.content
                placeholder.markdown(full_reply)

    # Save assistant message
    messages.append({"role": "assistant", "content": full_reply})