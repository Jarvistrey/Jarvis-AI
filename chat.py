import os
import openai
import json
import requests
import subprocess
import sys
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

# Import local modules if needed
# from prompt_engineering import get_prompt_template

# Configuration and paths
def get_config():
    """Load configuration from config.json"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

# OpenAI Implementation
def get_openai_response(prompt: str, api_key: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Get a response from OpenAI's model.
    
    Args:
        prompt: User's input
        api_key: OpenAI API key
        chat_history: Optional list of previous messages
        
    Returns:
        Response from OpenAI
    """
    try:
        openai.api_key = api_key
        
        # If no chat history provided, initialize with system message
        if not chat_history:
            chat_history = [
                {"role": "system", "content": "You are Jarvis, an AI assistant. Respond as if you were Tony Stark's AI."}
            ]
        
        # Make sure the prompt/user message is in the chat history
        user_message_exists = any(msg.get("role") == "user" and msg.get("content") == prompt for msg in chat_history[-5:])
        if not user_message_exists:
            chat_history.append({"role": "user", "content": prompt})
        
        # Only use the last 10 messages to avoid token limits
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=recent_history,
            max_tokens=800,
            temperature=0.7,
        )
        
        # Extract and return the response text
        message_content = response.choices[0].message["content"].strip()
        return message_content
    
    except Exception as e:
        print(f"Error getting OpenAI response: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

# Llama Implementation
def get_llama_response(prompt: str, model_path: str, system_prompt: str = None) -> str:
    """
    Get a response from the local Llama model.
    
    Args:
        prompt: User's input
        model_path: Path to the Llama model
        system_prompt: Optional system prompt
        
    Returns:
        Response from Llama
    """
    try:
        # Default system prompt if none provided
        if not system_prompt:
            system_prompt = "You are Jarvis, an AI assistant. Respond as if you were Tony Stark's AI."
        
        # Construct the full prompt for Llama
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nJarvis:"
        
        # Command to run Llama using llama.cpp
        # Adjust these parameters based on your specific llama.cpp installation
        cmd = [
            os.path.join(os.path.dirname(model_path), "llama-chat"),  # Adjust path to llama executable
            "-m", model_path,  # Model path
            "-n", "2048",  # Number of tokens to generate
            "-p", full_prompt,  # Prompt
            "--temp", "0.7",  # Temperature
            "--repeat_penalty", "1.1"  # Repetition penalty
        ]
        
        # Run the command and capture output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extract response from output
        # This might need adjustment based on how your llama.cpp outputs text
        response_text = result.stdout.strip()
        
        # Clean up the response - remove the prompt part
        if "Jarvis:" in response_text:
            response_text = response_text.split("Jarvis:")[1].strip()
        
        return response_text
    
    except subprocess.CalledProcessError as e:
        print(f"Error running Llama model: {e}")
        print(f"Stderr: {e.stderr}")
        return f"Sorry, I encountered an error with the Llama model: {str(e)}"
    except Exception as e:
        print(f"Error getting Llama response: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

# Alternative Llama implementation using Python bindings if available
def get_llama_response_py(prompt: str, model_path: str, system_prompt: str = None) -> str:
    """
    Alternative implementation using Python bindings for Llama if available.
    
    Args:
        prompt: User's input
        model_path: Path to the Llama model
        system_prompt: Optional system prompt
        
    Returns:
        Response from Llama
    """
    try:
        # Try to import llama_cpp
        # If not installed, you'll need: pip install llama-cpp-python
        from llama_cpp import Llama
        
        # Default system prompt if none provided
        if not system_prompt:
            system_prompt = "You are Jarvis, an AI assistant. Respond as if you were Tony Stark's AI."
        
        # Initialize Llama model
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,  # Context window size
            n_parts=1,  # Number of parts to split the model into
        )
        
        # Construct the prompt
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nJarvis:"
        
        # Generate response
        output = llm(
            full_prompt,
            max_tokens=512,
            stop=["User:", "\n\n"],
            temperature=0.7,
        )
        
        # Extract and return the generated text
        response_text = output["choices"][0]["text"].strip()
        return response_text
        
    except ImportError:
        print("llama-cpp-python not installed. Falling back to command-line method.")
        return get_llama_response(prompt, model_path, system_prompt)
    except Exception as e:
        print(f"Error getting Llama response via Python: {e}")
        # Fall back to command-line method
        return get_llama_response(prompt, model_path, system_prompt)

# Unified chat interface
def chat(prompt: str, model: str = "openai", chat_history: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Unified chat interface that routes to the appropriate model.
    
    Args:
        prompt: User's input
        model: Which model to use ("openai" or "llama")
        chat_history: Optional list of previous messages
        
    Returns:
        Response from the selected model
    """
    config = get_config()
    
    if model.lower() == "openai":
        api_key = config.get("openai_api_key")
        if not api_key:
            return "OpenAI API key not configured. Please check your config.json file."
        return get_openai_response(prompt, api_key, chat_history)
        
    elif model.lower() == "llama":
        model_path = config.get("llama_model_path")
        if not model_path:
            return "Llama model path not configured. Please check your config.json file."
        
        # Try Python bindings first, fall back to command-line
        try:
            from llama_cpp import Llama
            return get_llama_response_py(prompt, model_path)
        except ImportError:
            return get_llama_response(prompt, model_path)
    
    else:
        return f"Unknown model: {model}. Please use 'openai' or 'llama'."

# For testing purposes
if __name__ == "__main__":
    # Test OpenAI
    config = get_config()
    if config.get("openai_api_key"):
        print("Testing OpenAI...")
        response = chat("Tell me a joke about AI", "openai")
        print(f"OpenAI Response: {response}\n")
    
    # Test Llama
    if config.get("llama_model_path"):
        print("Testing Llama...")
        response = chat("Tell me a joke about AI", "llama")
        print(f"Llama Response: {response}")