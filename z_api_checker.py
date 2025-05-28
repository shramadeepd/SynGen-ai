import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === Configuration ===
API_KEY = os.getenv("SYNGEN_API_KEY")
BASE_URL = os.getenv("SYNGEN_BASE_URL")


# Claude 3.5 Sonnet
# Claude 3 Haiku
# Amazon Embedding v2

# === Prepare request payload ===
payload = {
    "api_key": API_KEY,
    "prompt": "Hello! Can you introduce yourself?",
    "model_id": "claude-3.5-sonnet",
    "model_params": {
        "max_tokens": 100,
        "temperature": 0.5
    }
}
headers = {
    "Content-Type": "application/json"
}

# === Send request ===
response = requests.post(BASE_URL, headers=headers, json=payload)

# === Handle response ===
if response.status_code == 200:
    data = response.json()
    # Extract generated text
    text = data["response"]["content"][0]["text"]
    print("Model response:")
    print(text)
else:
    print(f"Error {response.status_code}: {response.text}")
