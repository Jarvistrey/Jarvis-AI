import streamlit as st
import asyncio
from core.jarvis_core import JarvisCore

async def main():
    st.set_page_config(
        page_title="Jarvis AI",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Jarvis AI Assistant")
    
    # Initialize Jarvis if not already done
    if 'jarvis' not in st.session_state:
        st.session_state.jarvis = JarvisCore()
        st.session_state.messages = []

    # Chat input
    user_input = st.text_input("Message Jarvis:", key="user_input")
    
    if user_input:
        with st.spinner('Processing...'):
            response = await st.session_state.jarvis.process_input(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.write(f"You: {message['content']}")
        else:
            st.write(f"Jarvis: {message['content']}")

if __name__ == "__main__":
    asyncio.run(main())