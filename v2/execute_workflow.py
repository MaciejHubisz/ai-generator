import shutil
import time
from config import AGENTS, GENERATED_ROOT, CONTEXT_DIR, SENT_ROOT
from deepseek_wrapper import execute_prompt
from prompt_loader import load_prompt
from cache_manager import load_cached_response, save_cached_response, hash_prompt
from output_parser import extract_files_from_output
from file_writer import safe_write_file
from pathlib import Path


def clean_generated_folder():
    if GENERATED_ROOT.exists():
        print("🧹 Cleaning generated/ directory...")
        for item in GENERATED_ROOT.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        CONTEXT_DIR.mkdir(parents=True, exist_ok=True)


def load_generated_java_files() -> str:
    java_files = list(GENERATED_ROOT.rglob("*.java"))

    if not java_files:
        print("⚠️  No Java files found in generated/")
        return ""

    print(f"📁 Found {len(java_files)} Java file(s):")
    for path in java_files:
        print(f"   • {path.relative_to(GENERATED_ROOT)}")

    print("🧩 Injecting Java files into {{ files }} block...")

    output = []
    for path in java_files:
        code = path.read_text(encoding="utf-8")
        output.append(f"### FILE: {path}\n{code}")

    return "\n\n".join(output)


def run_agent(agent_name, prompt_path):
    print("\n" + "=" * 80)
    print(f"🔧 START AGENTA: {agent_name.upper()} — prompt: {prompt_path}")
    print("=" * 80 + "\n")

    # Specjalna obsługa agenta single_junit_agent
    if agent_name == "single_junit_agent":
        java_files = list(GENERATED_ROOT.rglob("*.java"))
        for java_file in java_files:
            print(f"\n📄 Processing file: {java_file}")
            file_content = java_file.read_text(encoding="utf-8")
            rel_path = java_file.relative_to(GENERATED_ROOT)

            extra_vars = {
                "file_path": str(rel_path),
                "file_content": file_content,
            }

            prompt = load_prompt(prompt_path, extra_vars=extra_vars)
            save_sent_prompt(agent_name, prompt)

            cached = load_cached_response(agent_name, prompt)
            if cached:
                output = cached
                print("🟢 Using cached result.")
            else:
                print("💸 Sending prompt to model...")
                try:
                    output = execute_prompt(prompt)
                    save_cached_response(agent_name, prompt, output)
                except Exception as e:
                    print(f"❌ Error: {e}")
                    continue

            files = extract_files_from_output(output)
            if not files:
                print("⚠️ No files extracted.")
                continue

            for rel_path, content in files.items():
                safe_write_file(rel_path, content)

            print(f"✅ Test generated for {java_file}")
        return

    # Standardowi agenci (jak dotąd)
    extra_vars = {}
    if agent_name == "junit_single_agent":
        extra_vars["files"] = load_generated_java_files()

    prompt = load_prompt(prompt_path, extra_vars=extra_vars if extra_vars else None)
    save_sent_prompt(agent_name, prompt)
    print(f"\n> Agent: {agent_name} | prompt: {prompt_path}")

    cached = load_cached_response(agent_name, prompt)
    if cached:
        print("🟢 Cached result used (no token cost)")
        output = cached
    else:
        print("💸 Sending prompt to model...")
        try:
            output = execute_prompt(prompt)
            print("✅ Model responded successfully.")
            save_cached_response(agent_name, prompt, output)
        except Exception as e:
            print(f"❌ {agent_name} failed: {type(e).__name__}: {e}")
            return

    print("📦 Extracting files from output...")
    files = extract_files_from_output(output)
    if not files:
        print("⚠️  No files to save.")
        return

    for rel_path, content in files.items():
        is_context_file = rel_path.startswith("context/")
        safe_write_file(rel_path, content, context_mode=is_context_file)

    print(f"\n✅ AGENT COMPLETED: {agent_name}")
    print("-" * 80)
    time.sleep(0.5)


def save_sent_prompt(agent_name: str, prompt_text: str):
    h = hash_prompt(prompt_text)
    prompt_dir = SENT_ROOT / agent_name
    prompt_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = prompt_dir / f"{h}.txt"
    prompt_path.write_text(prompt_text, encoding="utf-8")
    print(f"📝 Sent prompt saved: {prompt_path}")


if __name__ == "__main__":
    clean_generated_folder()
    for agent, ppath in AGENTS.items():
        run_agent(agent, ppath)
