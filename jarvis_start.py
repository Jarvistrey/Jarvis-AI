from core.jarvis_core import JarvisCore
import asyncio

def start_jarvis():
    """Initialize and start Jarvis"""
    jarvis = JarvisCore()
    
    if not jarvis.is_ready():
        print("❌ Error: LM Studio local server not detected")
        print("📝 Please:")
        print("1. Open LM Studio")
        print("2. Select model: llama-2-7b-chat")
        print("3. Start the local server")
        return None
    
    print("✅ Jarvis Core initialized and connected to LM Studio")
    return jarvis

if __name__ == "__main__":
    jarvis = start_jarvis()
    if jarvis:
        # Test the system
        response = asyncio.run(jarvis.process_input("Hello Jarvis, are you running locally?"))
        print("🤖 Response:", response)