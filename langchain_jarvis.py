import os
from dotenv import load_dotenv
from langchain_openai import OpenAI  # ✅ Final updated import

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def create_langchain_instance():
    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY not found. Make sure your .env file is in the root directory.")

    return OpenAI(api_key=api_key)  # ✅ Updated parameter name

if __name__ == "__main__":
    try:
        llm = create_langchain_instance()
        response = llm.invoke("Hello, who are you?")  # ✅ Uses updated LangChain Core interface
        print("🤖 JARVIS Response:", response)
    except Exception as e:
        print("⚠️ Error:", e)
