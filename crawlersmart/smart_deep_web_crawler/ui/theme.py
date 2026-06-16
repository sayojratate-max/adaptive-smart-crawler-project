import streamlit as st

COMMON_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Typography for entire app */
* {
    font-family: 'Inter', sans-serif !important;
}

/* Scrollbar Customization */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: rgba(150, 150, 150, 0.4);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(150, 150, 150, 0.6);
}

/* Sidebar Nav styling via Radio Buttons */
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
    padding: 10px 16px;
    background: transparent;
    border-radius: 12px;
    margin-bottom: 6px;
    transition: all 0.3s ease;
    border: 1px solid transparent;
}

section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
    background: var(--nav-hover-bg);
    transform: translateX(4px);
}

/* Selected Radio Button */
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] div:first-child {
    display: none; /* Hide default radio circle */
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size: 15px;
    font-weight: 500;
}

/* Hide Top Bar padding slightly */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}

/* Streamlit Button */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
    border: none;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

/* Input Fields */
.stTextInput > div > div > input, .stSelectbox > div > div > div {
    border-radius: 8px !important;
    padding: 10px 14px !important;
}

/* Custom Modal/Card Classes (for app.py) */
.hero {
    padding: 30px 40px;
    border-radius: 20px;
    box-shadow: 0 10px 40px var(--shadow-color);
    margin-bottom: 24px;
    background: var(--hero-bg);
    color: var(--hero-text);
    border: 1px solid var(--border-color);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%; right: -50%; bottom: -50%;
    background: radial-gradient(circle, var(--glow-color) 0%, transparent 60%);
    opacity: 0.15;
    pointer-events: none;
}
.hero-title {font-size: 38px; font-weight: 800; margin: 0; line-height: 1.2; z-index: 1;}
.hero-sub {font-size: 16px; margin-top: 10px; opacity: 0.9; z-index: 1;}

.tag {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 500;
    margin-right: 8px;
    margin-top: 10px;
    background: var(--tag-bg);
    color: var(--tag-text);
    border: 1px solid var(--border-color);
    backdrop-filter: blur(4px);
}

.card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 30px var(--shadow-color);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 35px var(--shadow-color-hover);
}
.card h3 {margin: 0 0 8px 0; font-weight: 700; font-size: 20px;}
.small {opacity: 0.85; font-size: 14px; line-height: 1.5;}
.divider {height: 1px; background: var(--border-color); margin: 24px 0;}
.badge {
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    background: var(--badge-bg);
    color: var(--badge-text);
    border: 1px solid var(--border-color);
}

/* Login Modal Center Override */
.login-container {
    background: var(--card-bg);
    padding: 40px;
    border-radius: 24px;
    box-shadow: 0 20px 60px var(--shadow-color);
    border: 1px solid var(--border-color);
    text-align: center;
}
"""

THEMES = {
    "Light": """
    :root {
        --nav-hover-bg: #f1f5f9;
        --hero-bg: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        --hero-text: #0f172a;
        --border-color: #e2e8f0;
        --shadow-color: rgba(15, 23, 42, 0.06);
        --shadow-color-hover: rgba(15, 23, 42, 0.12);
        --tag-bg: #f8fafc;
        --tag-text: #334155;
        --card-bg: #ffffff;
        --badge-bg: #eff6ff;
        --badge-text: #2563eb;
        --glow-color: #3b82f6;
    }
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    h1, h2, h3, h4, p {
        color: #0f172a !important;
    }
    .stButton > button {
        background-color: #2563eb;
        color: #ffffff;
    }
    """,

    "Dark": """
    :root {
        --nav-hover-bg: #1e293b;
        --hero-bg: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        --hero-text: #f8fafc;
        --border-color: #334155;
        --shadow-color: rgba(0, 0, 0, 0.3);
        --shadow-color-hover: rgba(0, 0, 0, 0.5);
        --tag-bg: rgba(255,255,255,0.05);
        --tag-text: #e2e8f0;
        --card-bg: #1e293b;
        --badge-bg: rgba(124, 58, 237, 0.2);
        --badge-text: #a78bfa;
        --glow-color: #8b5cf6;
    }
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }
    h1, h2, h3, h4, p {
        color: #f8fafc !important;
    }
    .stButton > button {
        background-color: #6366f1;
        color: #ffffff;
    }
    """,

    "Neon": """
    :root {
        --nav-hover-bg: rgba(34, 255, 136, 0.1);
        --hero-bg: #000000;
        --hero-text: #22ff88;
        --border-color: #22ff88;
        --shadow-color: rgba(34, 255, 136, 0.2);
        --shadow-color-hover: rgba(34, 255, 136, 0.5);
        --tag-bg: rgba(34,255,136,0.1);
        --tag-text: #22ff88;
        --card-bg: rgba(0,0,0,0.6);
        --badge-bg: rgba(255, 0, 255, 0.2);
        --badge-text: #ff00ff;
        --glow-color: #22ff88;
    }
    .stApp {
        background-color: #050505;
        color: #22ff88;
        background-image: linear-gradient(rgba(34, 255, 136, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(34, 255, 136, 0.03) 1px, transparent 1px);
        background-size: 30px 30px;
    }
    section[data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid #22ff88;
        box-shadow: 2px 0 15px rgba(34, 255, 136, 0.1);
    }
    h1, h2, h3, h4, p {
        color: #22ff88 !important;
    }
    .stButton > button {
        background-color: transparent;
        color: #22ff88;
        border: 1px solid #22ff88;
        box-shadow: 0 0 10px rgba(34,255,136,0.4);
    }
    .stButton > button:hover {
        background-color: rgba(34,255,136,0.1);
        box-shadow: 0 0 20px rgba(34,255,136,0.8);
    }
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: rgba(0,0,0,0.5) !important;
        border: 1px solid #22ff88 !important;
        color: #22ff88 !important;
    }
    """
}

def theme_selector():
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"
        
    theme = st.sidebar.radio(
        "🎨 App Theme",
        list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.theme)
    )

    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.rerun()

    return theme

def apply_theme(theme_name):
    base_css = THEMES.get(theme_name, THEMES["Dark"])
    full_css = f"<style>{COMMON_CSS}\\n{base_css}</style>"
    st.markdown(full_css, unsafe_allow_html=True)
