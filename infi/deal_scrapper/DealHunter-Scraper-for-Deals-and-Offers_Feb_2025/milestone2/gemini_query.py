import os
import google.generativeai as genai
from dotenv import load_dotenv

# ✅ Load API Key correctly from .env file
load_dotenv(dotenv_path=".env", override=True)
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ API Key is missing! Please set GEMINI_API_KEY in your .env file.")

# Configure the Gemini API with the loaded API Key
genai.configure(api_key=API_KEY)

# ✅ Function to query Gemini API
def query_gemini(prompt, model_choice="gemini-2.0-flash"):
    """Queries Google Gemini AI and returns the response."""
    model = genai.GenerativeModel(model_choice)
    response = model.generate_content(prompt)
    return response.text.strip()

if __name__ == "__main__":
    prompt = "Tell me a joke."
    response = query_gemini(prompt)
    print("🤖 Gemini Response:", response)
