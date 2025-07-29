import yaml
from pathlib import Path
from config import CONTEXT_DIR

def load_context_snippets() -> dict:
    snippets = {}
    for ctx_file in CONTEXT_DIR.glob("*.txt"):
        key = ctx_file.stem
        snippets[f"{{{{ {key} }}}}"] = ctx_file.read_text(encoding="utf-8")
    return snippets

def load_prompt(path: str) -> str:
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    base_prompt = ""
    if "extends" in data:
        base_prompts = []
        if isinstance(data["extends"], str):
            data["extends"] = [data["extends"]]
        for base_file in data["extends"]:
            base_path = path.parent / base_file
            base_data = yaml.safe_load(base_path.read_text(encoding="utf-8"))
            base_prompts.append(base_data.get("prompt", ""))
        base_prompt = "\n".join(base_prompts)

    prompt_text = data["prompt"].replace("{{ base_prompt }}", base_prompt)

    for key, value in load_context_snippets().items():
        prompt_text = prompt_text.replace(key, value)

    return prompt_text
