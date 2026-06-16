from bs4 import BeautifulSoup
from pathlib import Path
import json

def extract_text_from_html(file_path: Path):
    html = file_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.text.strip() if soup.title else file_path.name
    text = soup.get_text(separator=" ", strip=True)
    return title, text

def extract_text_from_txt(file_path: Path):
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    return file_path.name, text

def extract_text_from_json(file_path: Path):
    raw = file_path.read_text(encoding="utf-8", errors="ignore").strip()

    # ✅ If file is empty
    if not raw:
        return file_path.name, "[EMPTY JSON FILE]"

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # ✅ If JSON is invalid
        return file_path.name, f"[INVALID JSON FILE]\n\nRAW CONTENT:\n{raw[:500]}"

    title = file_path.name
    text = json.dumps(data, indent=2, ensure_ascii=False)
    return title, text
