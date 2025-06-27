from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()
def ask_with_context(question, context):
    llm = ChatOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama3-70b-8192"
    )
    prompt = f"Context: {context}\n\nQuestion: {question}"
    return llm.invoke(prompt).content
