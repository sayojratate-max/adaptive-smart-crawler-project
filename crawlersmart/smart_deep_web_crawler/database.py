import sqlite3
from pathlib import Path

# ✅ Always use project folder location, not terminal folder
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "output" / "crawler.db"

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        title TEXT,
        raw_text TEXT,
        summary TEXT,
        keywords TEXT,
        category TEXT,
        crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def reset_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS documents")
    conn.commit()
    conn.close()
    init_db()

def insert_document(source, title, raw_text, summary, keywords, category):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO documents (source, title, raw_text, summary, keywords, category)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (source, title, raw_text, summary, keywords, category))
    conn.commit()
    conn.close()

def fetch_all_documents():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, category, keywords, summary, crawled_at, source
        FROM documents
        ORDER BY crawled_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_document(doc_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM documents WHERE id=?", (doc_id,))
    row = cur.fetchone()
    conn.close()
    return row

def fetch_categories():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM documents WHERE category != ''")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return sorted(rows)

def search_documents(query="", category="All"):
    conn = get_conn()
    cur = conn.cursor()

    query = (query or "").strip().lower()

    sql = """
        SELECT id, title, category, keywords, summary, crawled_at, source
        FROM documents
        WHERE 1=1
    """
    params = []

    if category != "All":
        sql += " AND category = ?"
        params.append(category)

    if query:
        sql += """
            AND (
                lower(title) LIKE ?
                OR lower(raw_text) LIKE ?
                OR lower(summary) LIKE ?
                OR lower(keywords) LIKE ?
            )
        """
        like = f"%{query}%"
        params.extend([like, like, like, like])

    sql += " ORDER BY crawled_at DESC"
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_docs_for_embedding():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, raw_text, summary FROM documents ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    docs = []
    for doc_id, title, raw_text, summary in rows:
        # Combine fields so embeddings become powerful
        text = f"{title}\n\n{summary}\n\n{raw_text}"
        docs.append((doc_id, text))
    return docs
