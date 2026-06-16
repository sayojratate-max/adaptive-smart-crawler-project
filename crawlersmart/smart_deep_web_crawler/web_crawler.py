import requests
import feedparser
import wikipediaapi

from genai_processor import summarize, extract_keywords, classify_category
from database import insert_document


# ✅ IMPORTANT: Wikipedia blocks requests without proper User-Agent
USER_AGENT = "SmartDeepWebCrawler/1.0 (demo project; contact: student@example.com)"


# ---------------------- WIKIPEDIA SEARCH API ----------------------

def wiki_search(query: str, limit: int = 5):
    """
    Wikipedia Search API with proper User-Agent to avoid 403 Forbidden.
    Returns list of relevant Wikipedia page titles.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": limit
    }

    headers = {
        "User-Agent": USER_AGENT
    }

    r = requests.get(url, params=params, headers=headers, timeout=20)
    r.raise_for_status()

    data = r.json()
    titles = [item["title"] for item in data.get("query", {}).get("search", [])]
    return titles


def crawl_wikipedia(topic: str, max_pages: int = 5):
    """
    Crawl Wikipedia using top search results (relevant pages only).
    This avoids random internal links like .zip.
    """
    topic = (topic or "").strip()
    if not topic:
        print("❌ Empty topic for Wikipedia crawl")
        return

    # ✅ wikipediaapi also needs proper user agent
    wiki = wikipediaapi.Wikipedia(
        language="en",
        user_agent=USER_AGENT
    )

    titles = wiki_search(topic, limit=max_pages)

    if not titles:
        print("❌ No Wikipedia results found for:", topic)
        return

    inserted = 0

    for title in titles:
        page = wiki.page(title)

        if not page.exists():
            continue

        text = (page.text or "").strip()
        if not text:
            continue

        text = text[:8000]  # limit huge pages
        source = page.fullurl

        insert_document(
            source=source,
            title=page.title,
            raw_text=text,
            summary=summarize(text),
            keywords=extract_keywords(text),
            category=classify_category(text)
        )
        inserted += 1

    print(f"✅ Wikipedia crawl done: {inserted} relevant pages inserted")


# ---------------------- ARXIV ----------------------

def crawl_arxiv(topic: str, max_papers: int = 5):
    """
    Crawl arXiv research papers using arXiv API (Atom feed).
    Extract title + abstract + link.
    """
    topic = (topic or "").strip()
    if not topic:
        print("❌ Empty topic for arXiv crawl")
        return

    query = topic.replace(" ", "+")
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_papers}"

    feed = feedparser.parse(url)

    inserted = 0
    for entry in feed.entries:
        title = entry.title
        abstract = entry.summary
        link = entry.link

        raw_text = f"TITLE: {title}\n\nABSTRACT:\n{abstract}\n\nLINK:\n{link}"

        insert_document(
            source=link,
            title=title,
            raw_text=raw_text,
            summary=summarize(abstract),
            keywords=extract_keywords(abstract),
            category="Research Papers"
        )
        inserted += 1

    print(f"✅ arXiv crawl done: {inserted} papers inserted")
