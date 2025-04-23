import openai
import os
import json
import subprocess
import sys
from pathlib import Path

def get_config():
    """Load configuration from config.json"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def get_openai_response(prompt, api_key, chat_history=None):
    """Get a response from OpenAI's model."""
    try:
        openai.api_key = api_key
        
        if not chat_history:
            chat_history = [
                {"role": "system", "content": "You are Jarvis, an AI assistant. Respond as if you were Tony Stark's AI."}
            ]
        
        if chat_history[-1].get("role") != "user" or chat_history[-1].get("content") != prompt:
            chat_history.append({"role": "user", "content": prompt})
        
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=recent_history,
            max_tokens=800,
            temperature=0.7,
        )
        
        message_content = response.choices[0].message["content"].strip()
        return message_content
    
    except Exception as e:
        print(f"Error getting OpenAI response: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

def get_llama_response(prompt, model_path, system_prompt=None):
    """Get a response from the local Llama model."""
    try:
        if not system_prompt:
            system_prompt = "You are Jarvis, an AI assistant. Respond as if you were Tony Stark's AI."
        
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nJarvis:"
        
        cmd = [
            "llama-chat",  # Adjust path if needed
            "-m", model_path,
            "-n", "2048",
            "-p", full_prompt,
            "--temp", "0.7",
            "--repeat_penalty", "1.1"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        response_text = result.stdout.strip()
        
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

def chat(prompt, model="openai", chat_history=None):
    """Unified chat interface that routes to the appropriate model."""
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
        return get_llama_response(prompt, model_path)
    
    else:
        return f"Unknown model: {model}. Please use 'openai' or 'llama'."

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