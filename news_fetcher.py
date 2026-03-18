import feedparser

RSS_FEEDS = [
    "https://www.reuters.com/business/energy/rss",
    "https://www.investing.com/rss/news_commodities.rss"
]

def get_oil_news():
    news_list = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            news_list.append({
                "title": entry.title,
                "description": entry.get("summary", "")
            })

    return news_list[:10]
