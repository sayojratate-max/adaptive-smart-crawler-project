import re
from collections import Counter

STOPWORDS = set("""
a an the is are was were in on at to for and or of by from with as
this that these those be been being it its into about
""".split())

def summarize(text, max_sentences=2):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return " ".join(sentences[:max_sentences]) if sentences else text[:200]

def extract_keywords(text, top_n=6):
    words = re.findall(r"[A-Za-z]{3,}", text.lower())
    words = [w for w in words if w not in STOPWORDS]
    counts = Counter(words)
    return ", ".join([w for w, _ in counts.most_common(top_n)])

def classify_category(text):
    t = text.lower()
    if "tender" in t or "budget" in t:
        return "Government Tenders"
    if "scholarship" in t or "eligibility" in t:
        return "Education & Scholarship"
    if "health" in t or "flu" in t or "vaccination" in t:
        return "Health Bulletin"
    if "cyber" in t or "phishing" in t or "otp" in t:
        return "Cyber Crime"
    return "General"
