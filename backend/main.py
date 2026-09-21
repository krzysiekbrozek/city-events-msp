import sqlite3
import feedparser

RSS_URL = "https://news.google.com/rss?hl=pl&gl=PL&ceid=PL:pl"
DB_NAME = "events.db"


def init_db():
    """Tworzy bazę danych i tabelę na wydarzenia, jeśli jeszcze nie istnieją."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS events
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       title
                       TEXT
                       NOT
                       NULL,
                       published
                       TEXT,
                       link
                       TEXT
                       UNIQUE
                       NOT
                       NULL
                   )
                   """)
    conn.commit()
    conn.close()


def save_event(title, published, link):
    """Zapisuje pojedyncze wydarzenie do bazy, ignorując duplikaty."""
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
        # Link już istnieje w bazie (ignorujemy duplikat)
        return False
    finally:
        conn.close()


def fetch_and_store_events():
    """Pobiera dane z RSS i zapisuje je do bazy."""
    init_db()
    feed = feedparser.parse(RSS_URL)

    if feed.bozo:
        print("Błąd podczas pobierania RSS.")
        return

    added_count = 0
    for entry in feed.entries:
        title = entry.get("title", "Brak tytułu")
        link = entry.get("link", "")
        published = entry.get("published", "Brak daty")

        if link:
            if save_event(title, published, link):
                added_count += 1

    print(f"Pobrano wpisów: {len(feed.entries)}")
    print(f"Zapisano nowych w bazie danych: {added_count}")


if __name__ == "__main__":
    fetch_and_store_events()