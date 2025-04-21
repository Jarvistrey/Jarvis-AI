from dotenv import load_dotenv
import os

def test_env_key():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    print("Raw key representation:", repr(api_key))  # Reveals hidden characters

    if api_key:
        print("✅ API Key loaded.")
    else:
        print("❌ API Key not found.")

if __name__ == "__main__":
    test_env_key()
