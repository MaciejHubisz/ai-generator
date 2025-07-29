import re

def extract_files_from_output(text: str) -> dict:
    files = {}
    pattern = re.compile(
        r"### BEGIN FILE:\s*(.*?)\n(.*?)### END FILE",
        re.DOTALL
    )

    for match in pattern.finditer(text):
        path = match.group(1).strip()
        content = match.group(2).strip()
        if path:
            files[path] = content

    return files
