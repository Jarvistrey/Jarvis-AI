import requests
import json
import sys
from pathlib import Path

def test_llama_connection():
    """Test LM Studio Llama connection"""
    print("🔄 Testing LM Studio connection...\n")
    
    url = "http://127.0.0.1:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "messages": [
            {"role": "system", "content": "You are Jarvis, an AI assistant running on local LLM."},
            {"role": "user", "content": "Confirm you're running locally and explain what you can do."}
        ],
        "model": "llama-2-7b-chat",
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        print(f"📡 Connecting to LM Studio at: {url}")
        response = requests.post(url, headers=headers, json=data)
        print(f"📊 Status: {response.status_code}\n")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Connection successful!")
            print("\n🤖 Jarvis Response:")
            print(result["choices"][0]["message"]["content"])
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_llama_connection()
    sys.exit(0 if success else 1)