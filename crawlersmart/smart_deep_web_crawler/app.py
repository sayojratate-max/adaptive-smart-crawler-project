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
    fetch_docs_for_embedding,
)
from crawler import crawl_dataset
from web_crawler import crawl_wikipedia, crawl_arxiv
from semantic_search import build_faiss_index, semantic_search
from document_analyzer import analyze_document

# ------------------ Page Setup ------------------
st.set_page_config(
    page_title="Intelligent Web Crawler",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ Theme Management ------------------
if "theme" not in st.session_state:
    st.session_state.theme = "Cyan Neon"

THEMES = {
    "Cyan Neon": {"hex": "#00ffc4", "rgb": "0,255,196"},
    "Yellow Neon": {"hex": "#ffff00", "rgb": "255,255,0"},
    "Green Neon": {"hex": "#39ff14", "rgb": "57,255,20"}
}

c_hex = THEMES[st.session_state.theme]["hex"]
c_rgb = THEMES[st.session_state.theme]["rgb"]

# ------------------ Inject Cyber CSS ------------------
css_template = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@400;600&display=swap');

/* Global styles */
.stApp {
    background-color: #080f15;
    color: #ffffff;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background-color: #050a0f !important;
    border-right: 1px solid rgba(0,255,196,0.2) !important;
}

/* Sidebar Radio Buttons */
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
    gap: 14px;
}
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
    border: 1px solid rgba(0,255,196,0.6);
    border-radius: 20px;
    padding: 12px 15px;
    background-color: transparent;
    transition: all 0.3s ease;
    cursor: pointer;
    display: flex;
    align-items: center;
}
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
    box-shadow: inset 0 0 15px rgba(0,255,196,0.2);
}

/* Ensure text is visible */
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label p {
    color: #00ffc4 !important;
    font-weight: 600;
    margin: 0;
    width: 100%;
}

/* Active State */
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:has(input:checked),
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:has(div[aria-checked="true"]),
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:has([data-checked="true"]) {
    background-color: #00ffc4 !important;
    box-shadow: 0 0 20px rgba(0,255,196,0.5) !important;
    border: 1px solid #00ffc4 !important;
}

[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:has(input:checked) p,
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:has(div[aria-checked="true"]) p,
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:has([data-checked="true"]) p {
    color: #000000 !important;
    font-weight: 800 !important;
}

/* Hide standard circle safely */
[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label > div:first-of-type:not(:has(p)) {
    display: none !important;
}

/* Title Box */
.cyber-title-box {
    border: 1px solid #00ffc4;
    padding: 50px 40px;
    margin-top: 10px;
    margin-bottom: 20px;
    background-color: transparent;
}
.cyber-title {
    color: #00ffc4;
    font-family: 'Orbitron', sans-serif;
    text-shadow: 0 0 20px rgba(0,255,196,0.6);
    text-transform: uppercase;
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 25px;
    letter-spacing: 2px;
    line-height: 1.3;
}
.cyber-subtitle {
    color: #e2e8f0;
    font-size: 0.95rem;
    margin-bottom: 30px;
    letter-spacing: 0.5px;
}
.cyber-tag {
    border: 1px solid #00ffc4;
    border-radius: 20px;
    padding: 6px 18px;
    color: #00ffc4;
    font-size: 0.75rem;
    text-transform: uppercase;
    font-weight: 700;
    display: inline-block;
    margin-right: 12px;
    margin-bottom: 10px;
    background-color: transparent;
}
.cyber-tag:hover {
    box-shadow: 0 0 10px rgba(0,255,196,0.3);
}

/* Default standard headers applied globally */
h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; color: #00ffc4 !important; }

/* standard buttons */
.stButton > button {
    border: 1px solid rgba(0,255,196,0.5);
    border-radius: 12px;
    color: #ffffff;
    transition: 0.3s;
}
.stButton > button:hover {
    border-color: #00ffc4;
    box-shadow: 0 0 10px rgba(0,255,196,0.3);
    color: #00ffc4;
}

/* Center elements */
.block-container { padding-top: 2rem !important; }

/* Form inputs styling */
.stTextInput > div > div > input, .stSelectbox > div > div > div {
    border: 1px solid rgba(0,255,196,0.4) !important;
    background-color: rgba(0,0,0,0.5) !important;
    color: #00ffc4 !important;
}
</style>
"""

dynamic_css = css_template.replace("#00ffc4", c_hex).replace("0,255,196", c_rgb)
st.markdown(dynamic_css, unsafe_allow_html=True)


# ------------------ Paths ------------------
BASE_DIR = Path(__file__).resolve().parent
AUTH_DB = BASE_DIR / "output" / "auth.db"

# ------------------ Init Databases ------------------
init_db()

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

def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode("utf-8")).hexdigest()

def create_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(AUTH_DB)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users(username, password_hash) VALUES(?,?)", (username, hash_password(password)))
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
    if not row: return False
    return row[0] == hash_password(password)

# ------------------ Session State ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "🏠 DASHBOARD OVERVIEW"

# ------------------ LOGIN / SIGNUP ------------------
if not st.session_state.logged_in:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        with st.container(border=True):
            st.markdown(f"<h1 style='text-align: center; color:{c_hex}; font-family:Orbitron;'>🔐 SYSTEM AUTH</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #a0aec0;'>Provide credentials to access quantum crawler nodes.</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["🚀 Login", "📝 Sign Up"])

            with tab1:
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                rm = st.checkbox("Remember me", value=True)
                
                if st.button("Authenticate", use_container_width=True):
                    if not u.strip() or not p:
                        st.warning("⚠️ Please provide both username and password.")
                    elif validate_login(u.strip(), p):
                        st.session_state.logged_in = True
                        st.success("Access Granted!")
                        st.rerun()
                    else:
                        st.error("Access Denied. Invalid credentials.")

            with tab2:
                nu = st.text_input("New Username")
                np = st.text_input("New Password", type="password")
                np2 = st.text_input("Confirm Password", type="password")

                if st.button("Register Node", use_container_width=True):
                    if not nu.strip() or not np:
                        st.warning("⚠️ All fields are required.")
                    elif len(nu.strip()) < 4:
                        st.error("❌ Username must be at least 4 characters long.")
                    elif len(np) < 6:
                        st.error("❌ Password must be at least 6 characters long.")
                    elif not any(char.isdigit() for char in np) or not any(char.isalpha() for char in np):
                        st.error("❌ Password must contain at least one letter and one number.")
                    elif np != np2:
                        st.error("❌ Passwords do not match.")
                    else:
                        if create_user(nu.strip(), np):
                            st.success("✅ Node registered successfully! Please authenticate.")
                        else:
                            st.error("❌ Node already exists. Try a different username.")

    st.stop()

# ------------------ Pages ------------------
PAGES = [
    "🏠 DASHBOARD OVERVIEW", 
    "🕷️ Dynamic Crawl Center", 
    "📤 Document Upload", 
    "🔎 Intelligence Explorer", 
    "📄 Document Studio", 
    "📈 System Analytics", 
    "⬇️ Output Export"
]

with st.sidebar:
    st.markdown("<div style='display:flex; align-items:center; gap:10px;'><h3 style='margin:0;'><span style='font-size:24px;'>🧭</span> Main Navigation</h3></div><br>", unsafe_allow_html=True)
    page = st.radio("Go to", PAGES, index=PAGES.index(st.session_state.page), label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Theme Selection
    current_theme_index = list(THEMES.keys()).index(st.session_state.theme)
    chosen_theme = st.selectbox("🎨 Interface Theme", list(THEMES.keys()), index=current_theme_index)
    if chosen_theme != st.session_state.theme:
        st.session_state.theme = chosen_theme
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧨 Purge DB", use_container_width=True):
            reset_db()
            st.success("Database Purged")
            st.rerun()
    with c2:
        if st.button("🔓 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.page = "🏠 DASHBOARD OVERVIEW"
            st.rerun()

st.session_state.page = page

# ------------------ Helpers ------------------
def load_df(category="All", query=""):
    rows = search_documents(query=query, category=category)
    return pd.DataFrame(rows, columns=["ID", "Title", "Category", "Keywords", "Summary", "Crawled At", "Source"])

def rebuild_semantic_index():
    docs = fetch_docs_for_embedding()
    return build_faiss_index(docs)

# ------------------ PAGE: HOME ------------------
if page == "🏠 DASHBOARD OVERVIEW":
    st.markdown("""
    <div class="cyber-title-box">
        <div class="cyber-title">UNIFIED INTELLIGENT ADAPTIVE WEB CRAWLER</div>
        <div class="cyber-subtitle">Hyper-advanced web scraping • Vector-spaced AI intelligence • Real-time semantic analysis</div>
        <div>
            <span class="cyber-tag">QUANTUM SEARCH</span>
            <span class="cyber-tag">ENCRYPTED AUTH</span>
            <span class="cyber-tag">FAISS INDEX</span>
            <span class="cyber-tag">WEB & DB OPS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    df = load_df()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container(border=True):
            st.metric("Total Documents", len(df))
    with col2:
        with st.container(border=True):
            st.metric("Categories", df['Category'].nunique() if len(df) else 0)
    with col3:
        with st.container(border=True):
            st.metric("Unique Sources", df['Source'].nunique() if len(df) else 0)
    with col4:
        with st.container(border=True):
            st.metric("Last Crawl", df['Crawled At'].iloc[0][:10] if len(df) else 'N/A')

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1, 1])
    with left:
        with st.container(border=True):
            st.subheader("🚀 System Capabilities")
            st.markdown("- Deep web scraping (Wikipedia, arXiv, Secure Sets)\n- AI-driven Natural Language Summary\n- High-dimensional Semantic embeddings\n- Advanced metric visualizations")
    with right:
        with st.container(border=True):
            st.subheader("🎯 Operations Protocol")
            st.markdown("1. Access **Dynamic Crawl Center**\n2. Designate search parameters\n3. Execute Crawl (auto-generates semantic vector space)\n4. Utilize **Intelligence Explorer** for insights")

# ------------------ PAGE: CRAWL CENTER ------------------
elif page == "🕷️ Dynamic Crawl Center":
    st.title("🕷️ Dynamic Crawl Center")

    with st.container(border=True):
        crawl_mode = st.selectbox("🌐 Target Node", ["Local Dataset", "Wikipedia", "arXiv Research"])
        
        topic = ""
        if crawl_mode in ["Wikipedia", "arXiv Research"]:
            topic = st.text_input("🔎 Search Vector", placeholder="E.g., Quantum computing, Cyber warfare...")

        max_items = st.slider("📦 Document Limit", 1, 20, 5)

        st.markdown("<br>", unsafe_allow_html=True)
        colA, colB = st.columns([1, 1])
        with colA:
            start = st.button("🚀 Execute Crawl", use_container_width=True)
        with colB:
            reset_fresh = st.button("🧨 System Reset + New Crawl", use_container_width=True)

    def do_crawl():
        with st.spinner("Extracting nodes..."):
            if crawl_mode == "Local Dataset":
                crawl_dataset()
            elif crawl_mode == "Wikipedia":
                if not topic.strip():
                    st.error("A search vector is required.")
                    return
                crawl_wikipedia(topic.strip(), max_pages=max_items)
            else:
                if not topic.strip():
                    st.error("A search vector is required.")
                    return
                crawl_arxiv(topic.strip(), max_papers=max_items)

        with st.spinner("Compiling semantic index..."):
            n = rebuild_semantic_index()

        st.success(f"✅ Extraction complete. {n} records safely stored.")

    if reset_fresh:
        reset_db()
        do_crawl()
    elif start:
        do_crawl()

# ------------------ PAGE: EXPLORE ------------------
elif page == "🔎 Intelligence Explorer":
    st.title("🔎 Intelligence Explorer")
    
    tab1, tab2 = st.tabs(["🔤 Exact Keyword Database", "🧠 Semantic Vector Search"])

    with tab1:
        with st.container(border=True):
            categories = ["All"] + fetch_categories()
            col1, col2 = st.columns([1, 2])
            with col1:
                selected_category = st.selectbox("📌 Filter Class", categories)
            with col2:
                query = st.text_input("🔍 Exact Search", placeholder="Identify strict text matches...")

            df = load_df(selected_category, query)
            st.dataframe(df[["ID", "Title", "Category", "Keywords", "Crawled At"]], use_container_width=True, hide_index=True)

    with tab2:
        with st.container(border=True):
            sem_q = st.text_input("🧠 Semantic Query", placeholder="Conceptual search...")
            
            if st.button("🔄 Regenerate FAISS Vector Space"):
                with st.spinner("Processing..."):
                    n = rebuild_semantic_index()
                st.success(f"Space created for {n} models.")

            if sem_q.strip():
                results = semantic_search(sem_q.strip(), top_k=10)
                if not results:
                    st.warning("No data found.")
                else:
                    df_all = load_df()
                    ids = [doc_id for doc_id, _ in results]
                    df_sem = df_all[df_all["ID"].isin(ids)].copy()
                    rank_map = {doc_id: score for doc_id, score in results}
                    df_sem["Score"] = df_sem["ID"].map(rank_map)
                    df_sem = df_sem.sort_values("Score", ascending=False)
                    st.dataframe(df_sem[["ID", "Title", "Category", "Score"]], use_container_width=True, hide_index=True)

# ------------------ PAGE: DOCUMENT STUDIO ------------------
elif page == "📄 Document Studio":
    st.title("📄 Document Studio")
    
    df = load_df()
    if len(df) == 0:
        st.warning("No documents found in vault.")
    else:
        df_small = df[["ID", "Title", "Category"]].copy()
        df_small["Display"] = df_small.apply(lambda r: f"[{r['ID']}] {r['Title']} ({r['Category']})", axis=1)

        pick = st.selectbox("📥 Decrypt Document", df_small["Display"].tolist())
        doc_id = int(pick.split("]")[0].replace("[", "").strip())

        doc = fetch_document(doc_id)
        if doc:
            _, source, title, raw_text, summary, keywords, category, crawled_at = doc

            with st.container(border=True):
                st.subheader(title)
                st.caption(f"SOURCE: {source} | CLASS: {category} | TIMESTAMP: {crawled_at}")
                st.divider()
                
                cA, cB = st.columns(2)
                with cA:
                    st.info(f"**AI INTELLIGENCE REPORT:**\n{summary}")
                with cB:
                    st.success(f"**EXTRACTED TAGS:**\n{keywords if keywords else 'None'}")
                
            st.markdown("### RAW DATA PAYLOAD")
            with st.container(border=True):
                st.text(raw_text)

# ------------------ PAGE: UPLOAD DOCUMENT ------------------
elif page == "📤 Document Upload":
    st.title("📤 Document Upload Module")
    
    with st.container(border=True):
        uploaded_file = st.file_uploader("Drop payload here", type=["pdf", "docx", "txt"])
        save_db = st.checkbox("Commit to Intelligence DB", value=True)

        if uploaded_file and st.button("🧠 Execute Analysis"):
            with st.spinner("Processing deep scan..."):
                try:
                    result = analyze_document(uploaded_file.name, uploaded_file.read(), save_to_db=save_db)
                    st.success("✅ Analysis Complete")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.info(f"**SUMMARY:**\n{result['summary']}")
                    with c2:
                        st.success(f"**KEYWORDS:**\n{result['keywords']}")
                        st.markdown(f"**CLASS:** `{result['category']}`")
                        
                    with st.expander("Examine Raw Trace"):
                        st.text(result["text"])
                except Exception as e:
                    st.error(f"Error: {e}")

# ------------------ PAGE: ANALYTICS ------------------
elif page == "📈 System Analytics":
    st.title("📈 System Analytics")
    df = load_df()
    if len(df) == 0:
        st.warning("Insufficient data.")
    else:
        with st.container(border=True):
            st.subheader("Data Class Distribution")
            cat_counts = df["Category"].value_counts()
            fig = plt.figure(figsize=(10, 4))
            fig.patch.set_alpha(0.0)
            ax = fig.add_subplot(111)
            ax.patch.set_alpha(0.0)
            ax.tick_params(colors=c_hex)
            ax.spines['bottom'].set_color(c_hex)
            ax.spines['left'].set_color(c_hex)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.bar(cat_counts.index, cat_counts.values, color=c_hex)
            plt.xticks(rotation=20, ha="right")
            st.pyplot(fig)

# ------------------ PAGE: EXPORT ------------------
elif page == "⬇️ Output Export":
    st.title("⬇️ Output Export")
    df = load_df()
    if len(df) == 0:
        st.warning("No data to export.")
    else:
        with st.container(border=True):
            st.dataframe(df, use_container_width=True, height=250)
            
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("📥 Stream CSV", df.to_csv(index=False).encode("utf-8"), "data.csv", "text/csv", use_container_width=True)
            with c2:
                st.download_button("📥 Stream JSON", df.to_json(orient="records", indent=2), "data.json", "application/json", use_container_width=True)
