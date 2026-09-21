import sqlite3
import feedparser
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

RSS_URL = "https://news.google.com/rss?hl=pl&gl=PL&ceid=PL:pl"
DB_NAME = "events.db"

app = FastAPI(title="City Events API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            published TEXT,
            link TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_event(title, published, link):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO events (title, published, link) VALUES (?, ?, ?)",
            (title, published, link)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def fetch_and_store_events():
    """Pobiera nowe dane z RSS i dodaje do bazy unikaty."""
    feed = feedparser.parse(RSS_URL)
    if feed.bozo:
        return

    for entry in feed.entries:
        title = entry.get("title", "Brak tytułu")
        link = entry.get("link", "")
        published = entry.get("published", "Brak daty")
        if link:
            save_event(title, published, link)

def get_all_events():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, published, link FROM events ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- Endpoints / Lifecycle ---

@app.on_event("startup")
def startup_event():
    init_db()
    fetch_and_store_events()  # Automatyczne odświeżenie danych przy starcie API

@app.get("/")
def read_root():
    return {"message": "City Events API is running"}

@app.get("/events")
def read_events():
    events = get_all_events()
    return {"count": len(events), "data": events}