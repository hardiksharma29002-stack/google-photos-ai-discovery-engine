import os
from dotenv import load_dotenv

load_dotenv()

def list_gemini():
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    print("Gemini Models:")
    try:
        models = client.models.list()
        for m in models:
            print(m.name)
    except Exception as e:
        print(f"Error: {e}")

def list_groq():
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    print("Groq Models:")
    try:
        models = client.models.list()
        for m in models.data:
            print(m.id)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_gemini()
    list_groq()
