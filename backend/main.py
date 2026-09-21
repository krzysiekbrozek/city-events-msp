import feedparser

# Przykładowy kanał RSS z wydarzeniami / newsami
RSS_URL = "https://news.google.com/rss?hl=pl&gl=PL&ceid=PL:pl"


def fetch_events():
    print(f"Pobieranie danych z: {RSS_URL}...\n")
    feed = feedparser.parse(RSS_URL)

    if feed.bozo:
        print("Wystąpił problem z parsowaniem kanału RSS.")
        return

    print(f"Znaleziono wpisów: {len(feed.entries)}\n")

    for entry in feed.entries[:5]:  # Wyświetl pierwsze 5
        title = entry.get("title", "Brak tytułu")
        link = entry.get("link", "Brak linku")
        published = entry.get("published", "Brak daty")

        print(f"📌 Tytuł: {title}")
        print(f"📅 Data: {published}")
        print(f"🔗 Link: {link}")
        print("-" * 40)


if __name__ == "__main__":
    fetch_events()