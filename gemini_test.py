import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Gemini API key not found!")
else:
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
       model="gemini-3.5-flash-lite",
        contents="You are RecoverAI, an AI assistant that helps subscription businesses recover failed payments. Introduce yourself in one sentence."
    )

    print(response.text)
