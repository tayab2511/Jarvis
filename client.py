import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_site_url = os.getenv("OPENROUTER_SITE_URL", "")
openrouter_site_name = os.getenv("OPENROUTER_SITE_NAME", "Jarvis Assistant")
openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-5.2")

if not openrouter_api_key:
    raise ValueError("OPENROUTER_API_KEY is missing. Add it in your .env file.")

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openrouter_api_key}",
}
if openrouter_site_url:
    headers["HTTP-Referer"] = openrouter_site_url
if openrouter_site_name:
    headers["X-OpenRouter-Title"] = openrouter_site_name

payload = {
    "model": openrouter_model,
    "messages": [
        {
            "role": "user",
            "content": "Explain how AI works in a few words",
        }
    ],
}

print("Waiting for 15 seconds to avoid rate limit...")
time.sleep(15)

response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)

if response.status_code == 200:
    print("Data mil gaya:")
    print(response.json())
else:
    print("Error aagaya. Status Code:", response.status_code)
    print(response.text)