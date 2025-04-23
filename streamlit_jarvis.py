import streamlit as st
import os
import json
import sys
from pathlib import Path

# Import your modules
from chat import chat, get_config
from voice import text_to_speech, recognize_speech

# Page configuration
st.set_page_config(
    page_title="Jarvis AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Load and save configuration
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
    st.session_state.config = get_config()
if "voice_output" not in st.session_state:
    st.session_state.voice_output = False

# Process user input
def process_user_input(user_input):
    # Add user message to both histories
    user_message = {"role": "user", "content": user_input}
    st.session_state.openai_messages.append(user_message)
    st.session_state.llama_messages.append(user_message)
    
    # Get response from active model
    active_model = st.session_state.active_model.lower()
    
    if active_model == "openai":
        try:
            chat_history = st.session_state.openai_messages
            response = chat(user_input, "openai", chat_history)
        except Exception as e:
            response = f"Error getting OpenAI response: {str(e)}"
    else:  # Llama
        try:
            response = chat(user_input, "llama")
        except Exception as e:
            response = f"Error getting Llama response: {str(e)}"
    
    # Add response to the appropriate chat history
    if active_model == "openai":
        st.session_state.openai_messages.append({"role": "assistant", "content": response})
        st.session_state.llama_messages.append({"role": "assistant", "content": "[OpenAI was used]"})
    else:
        st.session_state.llama_messages.append({"role": "assistant", "content": response})
        st.session_state.openai_messages.append({"role": "assistant", "content": "[Llama was used]"})
    
    # Voice output if enabled
    if st.session_state.voice_output:
        text_to_speech(response)
    
    return response

# Voice input function
def handle_voice_input():
    try:
        st.session_state.listening = True
        user_input = recognize_speech()
        st.session_state.listening = False
        
        if user_input:
            process_user_input(user_input)
            st.experimental_rerun()
    except Exception as e:
        st.error(f"Error with voice input: {str(e)}")
        st.session_state.listening = False

# Main app
def main():
    # Title and description
    st.title("Jarvis AI Assistant")
    st.subheader("Your dual-model AI assistant with OpenAI and Llama")
    
    # Sidebar
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
        
        # Settings
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
                new_config = {**st.session_state.config}
                new_config["openai_api_key"] = openai_api_key
                new_config["llama_model_path"] = llama_model_path
                
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
        
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.llama_messages:
                role = message["role"]
                content = message["content"]
                
                if role == "user":
                    st.markdown(f"**You:** {content}")
                else:
                    st.markdown(f"**Jarvis:** {content}")
    
    # Input section
    st.write("---")
    st.info(f"Active Model: {st.session_state.active_model}")
    
    col1, col2 = st.columns([7, 1])
    
    with col1:
        user_input = st.text_input("Message Jarvis:", key="text_input")
    
    with col2:
        voice_button = st.button("🎤 Voice")
        if voice_button:
            handle_voice_input()
    
    if user_input:
        process_user_input(user_input)
        st.session_state.text_input = ""
        st.experimental_rerun()

if __name__ == "__main__":
    main()