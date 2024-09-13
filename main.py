import feedparser
from flask import request, Flask, render_template
import time
app = Flask(__name__)
RSS_FEED = {
    "Hacker News": "https://news.ycombinator.com/rss",
    "CNBC": "https://www.cnbc.com/technology/",
    "YAHOO FINANCE": "https://finance.yahoo.com/quote/RSS.V/",
    "WALL STREET JOURNAL": "https://feeds.a.dj.com/rss/RSSWSJD.xml",
    "PROJECT UPDATES": "https://www.fao.org/in-action/rss/en/",
}


@app.route("/")
def index():
    articles = []
    for source, feed in RSS_FEED.items():
        parsed_feed = feedparser.parse(feed)
        for entry in parsed_feed.entries:
            # Check if 'published_parsed' exists, otherwise set it to None
            published_parsed = getattr(entry, 'published_parsed', None)
            articles.append((source, entry, published_parsed))

    # Sort articles, placing those without 'published_parsed' at the end
    articles = sorted(articles, key=lambda x: x[2] if x[2] is not None else time.struct_time([0] * 9), reverse=True)

    page = request.args.get("page", 1, type=int)
    per_page = 10
    total_articles = len(articles)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_articles = articles[start:end]

    return render_template(
        "index.html",
        articles=paginated_articles,
        page=page,
        total_pages=total_articles // per_page + 1,
    )


@app.route("/search")
def search():
    query = request.args.get("q")
    articles = []
    for source, feed in RSS_FEED.items():
        parsed_feed = feedparser.parse(feed)
        entries = [(source, entry) for entry in parsed_feed.entries]
        articles.extend(entries)

        results = [
            article for article in articles if query.lower() in article[1].title.lower()
        ]
        return render_template("searched_result.html", articles=results, query=query)


if __name__ == "__main__":
    app.run(debug=True)
