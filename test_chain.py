import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

# Load .env variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise EnvironmentError("❌ OPENAI_API_KEY not found. Verify your .env file is in the root directory.")

# Define a simple prompt template
prompt = PromptTemplate.from_template("What do you think of the singularity, {name}?")

# Initialize the model with API access
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Chain it together
chain: RunnableSequence = prompt | llm

# Execute chain
response = chain.invoke({"name": "Trey"})
print(f"🤖 JARVIS: {response.content}")
