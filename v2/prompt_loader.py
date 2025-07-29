import yaml
from pathlib import Path
from config import CONTEXT_DIR


def load_context_snippets() -> dict:
    snippets = {}
    for ctx_file in CONTEXT_DIR.glob("*.txt"):
        key = ctx_file.stem
        snippets[key] = ctx_file.read_text(encoding="utf-8")
    return snippets


def load_prompt(path: str, extra_vars: dict = None) -> str:
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    prompt_vars = {}

    # 1. Ładujemy extends + scalony base_prompt
    base_prompt_parts = []
    if "extends" in data:
        extends = data["extends"]
        if isinstance(extends, str):
            extends = [extends]
        for base_file in extends:
            base_path = path.parent / base_file
            base_data = yaml.safe_load(base_path.read_text(encoding="utf-8"))
            prompt_value = base_data.get("prompt", "")
            key = Path(base_file).stem
            prompt_vars[key] = prompt_value
            base_prompt_parts.append(prompt_value)
    prompt_vars["base_prompt"] = "\n".join(base_prompt_parts)

    # 2. Dodaj context/*.txt
    prompt_vars.update(load_context_snippets())

    # 3. Dodaj zmienne runtime (np. file_path, file_content)
    if extra_vars:
        for key, value in extra_vars.items():
            prompt_vars[key] = str(value) if value is not None else ""

    # 4. Podmień zmienne
    prompt_text = data["prompt"]
    for key, value in prompt_vars.items():
        placeholder = f"{{{{ {key} }}}}"
        prompt_text = prompt_text.replace(placeholder, value)

    return prompt_text
