from pathlib import Path
from extractor import extract_text_from_html, extract_text_from_txt, extract_text_from_json
from genai_processor import summarize, extract_keywords, classify_category
from database import insert_document

def crawl_dataset(dataset_dir="dataset"):
    dataset_dir = Path(dataset_dir)

    # Crawl HTML "hidden web"
    hidden_web = dataset_dir / "hidden_web"
    html_files = list(hidden_web.rglob("*.html"))

    for file in html_files:
        title, text = extract_text_from_html(file)
        summary = summarize(text)
        keywords = extract_keywords(text)
        category = classify_category(text)
        insert_document(str(file), title, text, summary, keywords, category)

    # Crawl TXT docs
    docs = dataset_dir / "documents"
    txt_files = list(docs.glob("*.txt"))
    for file in txt_files:
        title, text = extract_text_from_txt(file)
        summary = summarize(text)
        keywords = extract_keywords(text)
        category = classify_category(text)
        insert_document(str(file), title, text, summary, keywords, category)

    # Crawl JSON form data
    form_data = dataset_dir / "form_data"
    json_files = list(form_data.glob("*.json"))
    for file in json_files:
        print("📄 Reading JSON:", file)
        title, text = extract_text_from_json(file)
        summary = summarize(text)
        keywords = extract_keywords(text)
        category = classify_category(text)
        insert_document(str(file), title, text, summary, keywords, category)

    print(f"✅ Crawling Completed: {len(html_files)+len(txt_files)+len(json_files)} items harvested.")
