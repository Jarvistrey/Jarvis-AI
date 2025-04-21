import streamlit as st
import os
import time
from pathlib import Path
import json
import sys

# Add the path to `runnables` if necessary (this is for fallback if `langchain` is not installed correctly)
# You can update this path if langchain is installed in a non-standard location
sys.path.append(os.path.join(os.path.dirname(__file__), "env", "Lib", "site-packages"))

# Import necessary modules
from chat import get_openai_response, get_llama_response
from voice import listen_for_command, text_to_speech

# Import the process_command from langchain.runnables
# This should work if LangChain is correctly installed in your environment
try:
    from langchain.runnables import process_command
except ImportError:
    st.error("LangChain module not found. Please ensure LangChain is installed.")
    sys.exit(1)

from web_request import make_web_request
from functions import (
    get_current_time,
    get_current_date,
    search_web,
    get_weather,
    # Import any other functions you use
)

# Set page configuration
st.set_page_config(
    page_title="Jarvis AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Load configuration
def load_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading config: {e}")
        return {"openai_api_key": "", "llama_model_path": ""}

# Save configuration
def save_config(config_data):
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving config: {e}")
        return False

# Initialize session state
if "openai_messages" not in st.session_state:
    st.session_state.openai_messages = []
if "llama_messages" not in st.session_state:
    st.session_state.llama_messages = []
if "active_model" not in st.session_state:
    st.session_state.active_model = "OpenAI"
if "config" not in st.session_state:
    st.session_state.config = load_config()
if "voice_output" not in st.session_state:
    st.session_state.voice_output = False

# Function to process user input with both models
def process_user_input(user_input):
    # Add user message to both histories
    user_message = {"role": "user", "content": user_input}
    st.session_state.openai_messages.append(user_message)
    st.session_state.llama_messages.append(user_message)
    
    # Process command with brain if it's a command
    command_result = process_command(user_input)
    if command_result:
        response = command_result
    else:
        # Get response from active model
        active_model = st.session_state.active_model
        
        if active_model == "OpenAI":
            try:
                # Use your implementation to get OpenAI response
                openai_api_key = st.session_state.config.get("openai_api_key", "")
                if not openai_api_key:
                    response = "Error: OpenAI API key not configured. Please set it in the settings."
                else:
                    response = get_openai_response(user_input, openai_api_key, st.session_state.openai_messages)
            except Exception as e:
                response = f"Error getting OpenAI response: {str(e)}"
        else:  # Llama
            try:
                # Use your implementation to get Llama response
                llama_model_path = st.session_state.config.get("llama_model_path", "")
                if not llama_model_path:
                    response = "Error: Llama model path not configured. Please set it in the settings."
                else:
                    response = get_llama_response(user_input, llama_model_path)
            except Exception as e:
                response = f"Error getting Llama response: {str(e)}"
    
    # Add response to the appropriate chat history
    if st.session_state.active_model == "OpenAI":
        st.session_state.openai_messages.append({"role": "assistant", "content": response})
        # Mark in Llama chat that OpenAI was used
        st.session_state.llama_messages.append({"role": "assistant", "content": "[OpenAI was used]"})
    else:
        st.session_state.llama_messages.append({"role": "assistant", "content": response})
        # Mark in OpenAI chat that Llama was used
        st.session_state.openai_messages.append({"role": "assistant", "content": "[Llama was used]"})
    
    # If voice output is enabled, convert to speech
    if st.session_state.voice_output:
        text_to_speech(response)
    
    return response

# Voice input function using your implementation
def handle_voice_input():
    try:
        st.session_state.listening = True
        user_input = listen_for_command()
        st.session_state.listening = False
        
        if user_input:
            process_user_input(user_input)
            st.experimental_rerun()
    except Exception as e:
        st.error(f"Error with voice input: {str(e)}")
        st.session_state.listening = False

# UI Elements
def main():
    # Title and description
    st.title("Jarvis AI Assistant")
    st.subheader("Your dual-model AI assistant with OpenAI and Llama")
    
    # Sidebar for settings and controls
    with st.sidebar:
        st.title("Controls")
        
        # Model selection
        st.subheader("Model Selection")
        model_choice = st.radio(
            "Choose AI Model:",
            ("OpenAI", "Llama"),
            index=0 if st.session_state.active_model == "OpenAI" else 1
        )
        
        if model_choice != st.session_state.active_model:
            st.session_state.active_model = model_choice
            st.success(f"Switched to {model_choice} model")
        
        # Voice output toggle
        st.subheader("Voice Settings")
        voice_output = st.checkbox("Enable Voice Output", value=st.session_state.voice_output)
        if voice_output != st.session_state.voice_output:
            st.session_state.voice_output = voice_output
        
        # Settings section
        st.subheader("Configuration")
        with st.expander("API Settings"):
            openai_api_key = st.text_input(
                "OpenAI API Key", 
                value=st.session_state.config.get("openai_api_key", ""),
                type="password"
            )
            
            llama_model_path = st.text_input(
                "Llama Model Path",
                value=st.session_state.config.get("llama_model_path", "")
            )
            
            if st.button("Save Settings"):
                new_config = {
                    "openai_api_key": openai_api_key,
                    "llama_model_path": llama_model_path,
                    # Preserve other settings that might be in the config
                    **{k: v for k, v in st.session_state.config.items() 
                       if k not in ["openai_api_key", "llama_model_path"]}
                }
                
                if save_config(new_config):
                    st.session_state.config = new_config
                    st.success("Settings saved successfully!")
        
        # Clear chat button
        if st.button("Clear Chat History"):
            st.session_state.openai_messages = []
            st.session_state.llama_messages = []
            st.success("Chat history cleared")
    
    # Main chat interface with side-by-side display
    col1, col2 = st.columns(2)
    
    # OpenAI Chat Column
    with col1:
        st.header("OpenAI Chat")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.openai_messages:
                role = message["role"]
                content = message["content"]
                
                if role == "user":
                    st.markdown(f"**You:** {content}")
                else:
                    st.markdown(f"**Jarvis:** {content}")
    
    # Llama Chat Column
    with col2:
        st.header("Llama Chat")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.llama_messages:
                role = message["role"]
                content = message["content"]
                
                if role == "user":
                    st.markdown(f"**You:** {content}")
                else:
                    st.markdown(f"**Jarvis:** {content}")
    
    # Input section (common for both models)
    st.write("---")
    
    # Display which model is active
    st.info(f"Active Model: {st.session_state.active_model}")
    
    # Text and voice input options
    col1, col2 = st.columns([7, 1])
    
    with col1:
        user_input = st.text_input("Message Jarvis:", key="text_input")
    
    with col2:
        voice_button = st.button("🎤 Voice")
        if voice_button:
            handle_voice_input()
    
    if user_input:
        process_user_input(user_input)
        # Reset the input box
        st.session_state.text_input = ""
        st.experimental_rerun()

# Run the app
if __name__ == "__main__":
    main()
