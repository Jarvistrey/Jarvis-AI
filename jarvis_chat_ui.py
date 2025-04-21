import sys
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import OpenAI

# Force UTF-8 encoding globally

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Check if API key is available
if not api_key:
    st.error("OpenAI API key not found. Please check your .env file.")
    st.stop()

# Initialize OpenAI LLM
llm = OpenAI(openai_api_key=api_key)

# Setup Streamlit UI
st.set_page_config(page_title="Jarvis V1 Chat", page_icon="🤖")
st.title("🤖 Jarvis V1 - AI Interface")
st.markdown("Ask me anything, human!")

# Sanitize to remove problematic Unicode characters but handle better
def sanitize(text):
    if not isinstance(text, str):
        return ""
    try:
        # Encoding in utf-8 and decode back to ensure proper handling
        return text.encode("utf-8", "ignore").decode("utf-8")
    except Exception as e:
        st.error(f"Error sanitizing input/output: {e}")
        return ""

# Get input from user
raw_input = st.text_input("You:", placeholder="Ask Jarvis anything...")

# Sanitize user input
user_input = sanitize(raw_input)

# Warn if something was removed
if raw_input != user_input and raw_input.strip() != "":
    st.warning("Some special characters were removed to avoid encoding issues.")

# Process input
if user_input:
    with st.spinner("Jarvis is thinking..."):
        try:
            # Get response from LLM
            response = llm.invoke(user_input)

            # Sanitize response just in case
            clean_response = sanitize(response)

            st.markdown(f"**Jarvis:** {clean_response}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
