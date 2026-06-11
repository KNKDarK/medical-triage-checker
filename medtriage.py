from datetime import datetime
import sqlite3
import hashlib
import re
import streamlit as st

DB_PATH = "medtriage_users.db"


@st.cache_resource
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )
    conn.commit()
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def validate_email(email: str) -> bool:
    return re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email) is not None


def signup_user(username: str, email: str, password: str) -> tuple[bool, str]:
    if not username.strip():
        return False, "Username is required."
    if len(username.strip()) < 3:
        return False, "Username must be at least 3 characters."
    if not re.match(r"^[a-zA-Z0-9_]+$", username.strip()):
        return False, "Username can only contain letters, numbers, and underscores."
    if not validate_email(email):
        return False, "Invalid email format."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username.strip(), email.strip(), hash_password(password), datetime.now().isoformat()),
        )
        conn.commit()
        return True, "Account created successfully! Please log in."
    except sqlite3.IntegrityError:
        return False, "Username or email already exists."


def login_user(username: str, password: str) -> tuple[bool, str]:
    conn = get_db()
    cur = conn.execute(
        "SELECT username, email FROM users WHERE username = ? AND password_hash = ?",
        (username.strip(), hash_password(password)),
    )
    row = cur.fetchone()
    if row:
        return True, row[1]
    return False, ""
