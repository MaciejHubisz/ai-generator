import hashlib
from pathlib import Path
from config import CACHE_ROOT

def hash_prompt(prompt_text: str) -> str:
    return hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()

def get_cache_path(agent_name: str, prompt_text: str) -> Path:
    h = hash_prompt(prompt_text)
    agent_cache_dir = CACHE_ROOT / agent_name
    agent_cache_dir.mkdir(parents=True, exist_ok=True)
    return agent_cache_dir / f"{h}.json"

def load_cached_response(agent_name: str, prompt_text: str) -> str | None:
    path = get_cache_path(agent_name, prompt_text)
    if path.exists():
        print(f"💾 Using cached result for prompt: {path.name}")
        return path.read_text(encoding="utf-8")
    print(f"🆕 Cache miss: {path.name}")
    return None

def save_cached_response(agent_name: str, prompt_text: str, response: str):
    path = get_cache_path(agent_name, prompt_text)
    path.write_text(response, encoding="utf-8")
    print(f"📝 Cached result saved: {path.name}")
