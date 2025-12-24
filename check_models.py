import google.generativeai as genai
import os

# Configure using your .env key
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

print("--- AVAILABLE MODELS ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Name: {m.name}")
except Exception as e:
    print(f"Error: {e}")
print("------------------------")