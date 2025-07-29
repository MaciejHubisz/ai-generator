import os

import requests
from cachetools import TTLCache, cached
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type, wait_fixed

load_dotenv()

API_URL = os.getenv("DEESEEK_BASE_URL", "https://api.deepseek.com/v1/chat/completions")
API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEFAULT_MODEL = "deepseek-chat"
CACHE = TTLCache(maxsize=128, ttl=3600)
MODEL = "deepseek-chat"
TIMEOUT = 60
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

if not API_KEY:
    raise RuntimeError("DEEPSEEK_API_KEY is required")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def execute_prompt(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a senior software developer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }

    print("📡 Wysyłanie zapytania do DeepSeek...")
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=TIMEOUT)

    if response.status_code != 200:
        print(f"❌ HTTP {response.status_code}: {response.text}")
    response.raise_for_status()

    data = response.json()

    # ✅ Loguj tokeny
    if "usage" in data:
        usage = data["usage"]
        print(f"📊 Tokeny: prompt={usage['prompt_tokens']}, completion={usage['completion_tokens']}, total={usage['total_tokens']}")
    else:
        print("⚠️ Brak danych o tokenach w odpowiedzi.")

    # ✅ Wyciągnij odpowiedź modelu
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError("⚠️ Nieprawidłowa struktura odpowiedzi API.")
