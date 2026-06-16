import sqlite3
import hashlib
from pathlib import Path

# ------------------ DB Path ------------------
BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_DB = BASE_DIR / "output" / "auth.db"


# ------------------ Init Auth DB ------------------
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


# ------------------ Helpers ------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(username: str, password: str) -> bool:
    if not username or not password:
        return False

    conn = sqlite3.connect(AUTH_DB)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username.strip(), hash_password(password))
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
    cur.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username.strip(),)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return False

    return row[0] == hash_password(password)
