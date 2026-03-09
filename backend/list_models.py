import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    with open("models.txt", "w") as f:
        for model in client.models.list():
            f.write(f"{model.name}\n")
    print("Done writing models.txt")
except Exception as e:
    print(f"Error: {e}")
