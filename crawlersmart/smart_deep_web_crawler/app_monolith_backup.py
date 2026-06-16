import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from pathlib import Path
import hashlib

from database import (
    init_db,
    reset_db,
    fetch_document,
    fetch_categories,
    search_documents,
    fetch_docs_for_embedding,   # ✅ semantic
)
from crawler import crawl_dataset
from web_crawler import crawl_wikipedia, crawl_arxiv

# ✅ semantic search
from semantic_search import build_faiss_index, semantic_search
from document_analyzer import analyze_document



# ------------------ Page Setup ------------------
st.set_page_config(
    page_title="Smart Deep Web Crawler (GenAI)",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ Paths ------------------
BASE_DIR = Path(__file__).resolve().parent
AUTH_DB = BASE_DIR / "output" / "auth.db"

# ------------------ Vibrant CSS ------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');

* {font-family: 'Poppins', sans-serif;}
.block-container {padding-top: 1rem; padding-bottom: 2rem;}

.hero {
    padding: 22px 26px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(124,58,237,0.95), rgba(34,197,94,0.75));
    box-shadow: 0 18px 45px rgba(0,0,0,0.30);
    margin-bottom: 16px;
}
.hero-title {font-size: 34px; font-weight: 800; color: white; margin: 0;}
.hero-sub {font-size: 14px; color: rgba(255,255,255,0.92); margin-top: 6px;}

.tag {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    background: rgba(255,255,255,0.20);
    color: rgba(255,255,255,0.98);
    font-size: 12px;
    margin-right: 8px;
    border: 1px solid rgba(255,255,255,0.15);
}

.card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
}
.card h3 {margin: 0 0 6px 0; font-weight: 800;}
.small {opacity: 0.86; font-size: 13px;}
.divider {height: 1px; background: rgba(255,255,255,0.12); margin: 16px 0;}
.badge {
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 12px;
    background: rgba(124,58,237,0.22);
    border: 1px solid rgba(124,58,237,0.30);
}
</style>
""", unsafe_allow_html=True)


# ------------------ Init Databases ------------------
init_db()


# ------------------ Auth DB ------------------
def init_auth_db():
    AUTH_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(AUTH_DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    """)
    conn.commit()
    conn.close()


init_auth_db()


# ------------------ Auth Helpers ------------------
def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode("utf-8")).hexdigest()


def create_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(AUTH_DB)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users(username, password_hash) VALUES(?,?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def validate_login(username: str, password: str) -> bool:
    conn = sqlite3.connect(AUTH_DB)
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    return row[0] == hash_password(password)


# ------------------ Session State ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"


# ------------------ Hero Header ------------------
st.markdown("""
<div class="hero">
  <div class="hero-title">🕵️ Smart Deep Web Crawler (GenAI)</div>
  <div class="hero-sub">
    Crawl hidden sources • AI Summary • Keyword extraction • Category tagging • Semantic Search
  </div>
  <div style="margin-top:10px;">
    <span class="tag">✨ Vibrant UI</span>
    <span class="tag">🔐 Login System</span>
    <span class="tag">🧠 Semantic Search</span>
    <span class="tag">🌐 Wikipedia/arXiv</span>
    <span class="tag">🗄️ SQLite Storage</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ------------------ LOGIN / SIGNUP ------------------
if not st.session_state.logged_in:
    st.markdown("## 🔐 Login Required")

    tab1, tab2 = st.tabs(["✅ Login", "🆕 Sign Up"])

    with tab1:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            if validate_login(u.strip(), p):
                st.session_state.logged_in = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

    with tab2:
        nu = st.text_input("Create Username", key="signup_user")
        np = st.text_input("Create Password", type="password", key="signup_pass")
        np2 = st.text_input("Confirm Password", type="password", key="signup_pass2")

        if st.button("Create Account", use_container_width=True):
            if not nu.strip() or not np:
                st.error("Username & password required.")
            elif np != np2:
                st.error("Passwords do not match.")
            else:
                ok = create_user(nu.strip(), np)
                if ok:
                    st.success("✅ Account created! Now login.")
                else:
                    st.error("❌ Username already exists.")

    st.stop()


# ------------------ Pages ------------------
PAGES = ["🏠 Home", "🕷️ Crawl Center", "📤 Upload Document", "🔎 Explore", "📄 Document Studio", "📊 Analytics", "⬇️ Export"]

with st.sidebar:
    st.markdown("### 🕸️ Smart Crawler")
    st.caption("Logged in ✅")

    try:
        st.image("assets/logo.png", use_container_width=True)
    except:
        pass

    st.markdown("### 🧭 Navigation")
    page = st.radio(
        "Go to",
        PAGES,
        index=PAGES.index(st.session_state.page),
        label_visibility="collapsed"
    )

    st.markdown("---")
    if st.button("🧹 Reset Database", use_container_width=True):
        reset_db()
        st.success("Database reset ✅")
        st.rerun()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.page = "🏠 Home"
        st.rerun()

# persist page in session state
st.session_state.page = page


# ------------------ Helpers ------------------
def load_df(category="All", query=""):
    rows = search_documents(query=query, category=category)
    return pd.DataFrame(rows, columns=["ID", "Title", "Category", "Keywords", "Summary", "Crawled At", "Source"])


def rebuild_semantic_index():
    """
    Build FAISS index from DB documents.
    """
    docs = fetch_docs_for_embedding()
    n = build_faiss_index(docs)
    return n


# ------------------ PAGE: HOME ------------------
if page == "🏠 Home":
    df = load_df()

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='card'><h3>📄 {len(df)}</h3><div class='small'>Total Documents</div></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'><h3>📌 {df['Category'].nunique() if len(df) else 0}</h3><div class='small'>Categories</div></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'><h3>🧾 {df['Source'].nunique() if len(df) else 0}</h3><div class='small'>Unique Sources</div></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='card'><h3>🕒</h3><div class='small'>{df['Crawled At'].iloc[0] if len(df) else '-'}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("<div class='card'><h3>🚀 Features</h3>"
                    "<div class='small'>"
                    "• Crawl: Dataset / Wikipedia / arXiv<br>"
                    "• AI Summary + Keywords + Category<br>"
                    "• 🔥 Semantic Search using embeddings + FAISS<br>"
                    "• Search, Analytics, Export"
                    "</div></div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='card'><h3>🎯 Quick Start</h3>"
                    "<div class='small'>"
                    "1) Open Crawl Center<br>"
                    "2) Select source & keyword<br>"
                    "3) Start Crawl (auto builds semantic index)<br>"
                    "4) Explore & Semantic Search"
                    "</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    st.subheader("📌 Recent Documents")
    if len(df):
        st.dataframe(df[["ID", "Title", "Category", "Crawled At"]].head(12), use_container_width=True)
    else:
        st.info("No documents yet. Crawl something first.")


# ------------------ PAGE: CRAWL CENTER ------------------
elif page == "🕷️ Crawl Center":
    st.subheader("🕷️ Crawl Center")
    st.caption("Crawl sources and instantly preview results. Semantic index is built automatically.")

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    crawl_mode = st.selectbox("🌐 Crawl Mode", ["Local Dataset", "Wikipedia", "arXiv Research"])
    topic = ""
    if crawl_mode in ["Wikipedia", "arXiv Research"]:
        topic = st.text_input("🔎 Topic / Keyword", placeholder="Try: Cybercrime, Deep learning, Scholarship")

    max_items = st.slider("📦 Max Items", 1, 20, 5)

    colA, colB = st.columns([1, 1])
    with colA:
        start = st.button("🚀 Start Crawl", use_container_width=True)
    with colB:
        reset_fresh = st.button("🧨 Reset + Fresh Crawl", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    def do_crawl():
        with st.spinner("Crawling..."):
            if crawl_mode == "Local Dataset":
                crawl_dataset()
            elif crawl_mode == "Wikipedia":
                if not topic.strip():
                    st.error("Enter a topic for Wikipedia.")
                    return
                crawl_wikipedia(topic.strip(), max_pages=max_items)
            else:
                if not topic.strip():
                    st.error("Enter a topic for arXiv.")
                    return
                crawl_arxiv(topic.strip(), max_papers=max_items)

        with st.spinner("Building semantic index (FAISS)..."):
            n = rebuild_semantic_index()

        st.success(f"✅ Crawl done! Semantic index built for {n} documents. Opening Document Studio...")
        st.session_state.page = "📄 Document Studio"
        st.balloons()
        st.rerun()

    if reset_fresh:
        reset_db()
        st.info("Database reset ✅")
        do_crawl()

    if start:
        do_crawl()

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.subheader("📑 Latest Crawled Documents")
    df_latest = load_df()
    if len(df_latest):
        st.dataframe(df_latest[["ID", "Title", "Category", "Crawled At"]].head(20), use_container_width=True)
    else:
        st.info("No data yet. Crawl above.")


# ------------------ PAGE: EXPLORE ------------------
elif page == "🔎 Explore":
    st.subheader("🔎 Explore Documents")
    st.caption("Normal search = exact match. Semantic search = meaning-based (AI embeddings).")

    tab1, tab2 = st.tabs(["🔤 Normal Search", "🧠 Semantic Search"])

    # -------- Normal search
    with tab1:
        categories = ["All"] + fetch_categories()
        col1, col2 = st.columns([1, 2])
        with col1:
            selected_category = st.selectbox("📌 Category", categories)
        with col2:
            query = st.text_input("🔍 Normal Search", placeholder="exact words search")

        df = load_df(selected_category, query)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown(f"<span class='badge'>Results: {len(df)}</span>", unsafe_allow_html=True)
        st.dataframe(df[["ID", "Title", "Category", "Keywords", "Crawled At"]], use_container_width=True)

    # -------- Semantic search
    with tab2:
        sem_q = st.text_input("🧠 Semantic Search", placeholder="Search by meaning: online fraud, scholarship, security...")

        if st.button("🔄 Rebuild Semantic Index", use_container_width=True):
            with st.spinner("Rebuilding semantic index..."):
                n = rebuild_semantic_index()
            st.success(f"Semantic index built for {n} documents ✅")

        if sem_q.strip():
            results = semantic_search(sem_q.strip(), top_k=10)  # list (doc_id, score)

            if not results:
                st.warning("No semantic index found yet. Crawl again or press Rebuild Semantic Index.")
            else:
                df_all = load_df()
                ids = [doc_id for doc_id, _ in results]
                df_sem = df_all[df_all["ID"].isin(ids)].copy()

                rank_map = {doc_id: score for doc_id, score in results}
                df_sem["Score"] = df_sem["ID"].map(rank_map)
                df_sem = df_sem.sort_values("Score", ascending=False)

                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
                st.subheader("🎯 Semantic Results")
                st.dataframe(df_sem[["ID", "Title", "Category", "Score", "Crawled At"]], use_container_width=True)
        else:
            st.info("Type a semantic query to search by meaning.")


# ------------------ PAGE: DOCUMENT STUDIO ------------------
elif page == "📄 Document Studio":
    st.subheader("📄 Document Studio")
    st.caption("Open any document — see summary, keywords, and extracted text like a real viewer.")

    df = load_df()
    if len(df) == 0:
        st.warning("No documents found. Crawl first.")
    else:
        df_small = df[["ID", "Title", "Category"]].copy()
        df_small["Display"] = df_small.apply(lambda r: f"#{r['ID']} • {r['Title']}  ({r['Category']})", axis=1)

        pick = st.selectbox("📌 Choose Document", df_small["Display"].tolist())
        doc_id = int(pick.split("•")[0].replace("#", "").strip())

        doc = fetch_document(doc_id)
        if doc:
            _, source, title, raw_text, summary, keywords, category, crawled_at = doc

            st.markdown(f"### {title}")
            st.markdown(
                f"<span class='badge'>Category: {category}</span> &nbsp;&nbsp; "
                f"<span class='badge'>Crawled: {crawled_at}</span>",
                unsafe_allow_html=True
            )
            st.caption(f"Source: {source}")

            colA, colB = st.columns([1, 1])
            with colA:
                st.markdown("### 🤖 GenAI Summary")
                st.info(summary)
            with colB:
                st.markdown("### 🏷️ Keywords")
                st.success(keywords if keywords else "No keywords")

            st.markdown("### 📌 Extracted Text")
            st.text_area("Content", raw_text, height=360)

# ------------------ PAGE: UPLOAD DOCUMENT ------------------
elif page == "📤 Upload Document":
    st.subheader("📤 Upload Document & Get AI Summary")
    st.caption("Upload a PDF / DOCX / TXT file and instantly extract insights.")

    uploaded_file = st.file_uploader(
        "Upload document",
        type=["pdf", "docx", "txt"]
    )

    save_db = st.checkbox("Save analyzed document to database", value=True)

    if uploaded_file:
        if st.button("🧠 Analyze Document", use_container_width=True):
            with st.spinner("Analyzing document..."):
                try:
                    result = analyze_document(
                        uploaded_file.name,
                        uploaded_file.read(),
                        save_to_db=save_db
                    )

                    st.success("✅ Document analyzed successfully!")

                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.markdown("### 🤖 Summary")
                        st.info(result["summary"])

                    with col2:
                        st.markdown("### 🏷️ Keywords")
                        st.success(result["keywords"])
                        st.markdown(f"**Category:** `{result['category']}`")

                    st.markdown("### 📌 Extracted Text")
                    st.text_area("Content", result["text"], height=350)

                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ------------------ PAGE: ANALYTICS ------------------
elif page == "📊 Analytics":
    st.subheader("📊 Analytics")
    st.caption("Insights based on crawled content.")

    df = load_df()
    if len(df) == 0:
        st.warning("No data. Crawl first.")
    else:
        st.markdown("<div class='card'><h3>📌 Category Distribution</h3></div>", unsafe_allow_html=True)
        cat_counts = df["Category"].value_counts()

        fig = plt.figure()
        plt.bar(cat_counts.index, cat_counts.values)
        plt.xticks(rotation=25, ha="right")
        st.pyplot(fig)


# ------------------ PAGE: EXPORT ------------------
elif page == "⬇️ Export":
    st.subheader("⬇️ Export Center")
    st.caption("Download results instantly for reports, PPT, or submission.")

    df = load_df()
    if len(df) == 0:
        st.warning("No data to export.")
    else:
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download CSV",
                data=csv,
                file_name="crawler_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col2:
            json_data = df.to_json(orient="records", indent=2)
            st.download_button(
                "📥 Download JSON",
                data=json_data,
                file_name="crawler_results.json",
                mime="application/json",
                use_container_width=True
            )
