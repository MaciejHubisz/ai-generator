from pathlib import Path
from config import GENERATED_ROOT, CONTEXT_DIR

def safe_write_file(rel_path: str, content: str, context_mode=False):
    try:
        if not rel_path or rel_path.strip().endswith("/"):
            print(f"⚠️  Skipped invalid path: {rel_path}")
            return
        base_dir = CONTEXT_DIR if context_mode else GENERATED_ROOT
        clean_path = rel_path.strip()
        if context_mode and clean_path.startswith("context/"):
            clean_path = clean_path[len("context/"):]
        target_path = base_dir / clean_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
        print(f"✅ Saved: {target_path}")
    except Exception as e:
        print(f"❌ Write error for {rel_path}: {e}")
