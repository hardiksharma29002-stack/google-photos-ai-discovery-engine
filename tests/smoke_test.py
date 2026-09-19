import os
from dotenv import load_dotenv

load_dotenv()

def test_youtube():
    try:
        from googleapiclient.discovery import build
        api_key = os.getenv("YOUTUBE_API_KEY")
        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.search().list(part="snippet", q="google photos", maxResults=1)
        response = request.execute()
        print("[SUCCESS] YouTube API: OK (Successfully connected and ran a search)")
    except Exception as e:
        print(f"[FAIL] YouTube API Error: {e}")

def test_gemini():
    try:
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Say exactly this: '[SUCCESS] Gemini API: OK (Successfully connected and generated text)'"
        )
        print(response.text.strip())
    except Exception as e:
        print(f"[FAIL] Gemini API Error: {e}")

def test_groq():
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": "Say exactly this: '[SUCCESS] Groq API: OK (Successfully connected and generated text)'"}],
            model="groq/compound-mini",
        )
        print(chat_completion.choices[0].message.content.strip())
    except Exception as e:
        print(f"[FAIL] Groq API Error: {e}")

if __name__ == "__main__":
    print("Running Phase 0 Smoke Tests...")
    print("-" * 30)
    test_youtube()
    test_gemini()
    test_groq()
    print("-" * 30)
    print("Smoke tests complete.")
