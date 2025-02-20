import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
from datetime import datetime
from config import TELEGRAM_TOKEN, CHANNEL_ID, TARGET_URLS, SPOILER_TERMS
import json
from fuzzywuzzy import fuzz

async def post_to_telegram(bot, message):
    """Send a message to the Telegram channel."""
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=message, disable_web_page_preview=False)
        print(f"Posted at {datetime.now()}: {message[:50]}...")
    except Exception as e:
        print(f"Telegram error: {e}")

def is_spoiler_free(text):
    """Check if text contains match result spoilers."""
    text_lower = text.lower()
    return not any(term in text_lower for term in SPOILER_TERMS)

def load_history():
    """Load previously posted articles from file, capped at 7 days."""
    try:
        with open("posted.json", "r") as f:
            return json.load(f)  # List of [title, link, timestamp]
    except FileNotFoundError:
        return []

def save_history(history):
    """Save posted articles to file, pruning old entries."""
    cutoff = datetime.now().timestamp() - (7 * 24 * 60 * 60)  # 7 days ago
    history = [entry for entry in history if entry[2] > cutoff]
    with open("posted.json", "w") as f:
        json.dump(history, f)

def is_duplicate(new_title, new_link, history, threshold=85):
    """Check if article is a duplicate based on title similarity or exact link."""
    for old_title, old_link, _ in history:
        if new_link == old_link:
            return True
        if fuzz.token_sort_ratio(new_title, old_link) >= threshold:
            return True
    return False

def scrape_rugby_news():
    """Scrape headlines, snippets, and links from rugby news sites."""
    articles = []
    seen = set()
    history = load_history()
    headers = {"User-Agent": "Mozilla/5.0"}

    for url in TARGET_URLS:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            for item in soup.select(".article, .news-item, h2, .post-title"):
                title = item.get_text(strip=True)
                link = item.find("a")["href"] if item.find("a") else url
                snippet_tag = item.find_next("p") or item.find_next(".summary")
                snippet = snippet_tag.get_text(strip=True)[:150] + "..." if snippet_tag else ""

                article_key = f"{title}|{link}"
                if (title and is_spoiler_free(title + " " + snippet) and 
                    article_key not in seen and not is_duplicate(title, link, history)):
                    articles.append({"title": title, "snippet": snippet, "link": link})
                    seen.add(article_key)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    return articles

async def main():
    """Main function to scrape and post hourly."""
    bot = telegram.Bot(TELEGRAM_TOKEN)
    articles = scrape_rugby_news()
    history = load_history()

    for article in articles[:5]:  # Limit to 5 posts
        message = f"**Headline:** {article['title']}\n**Snippet:** {article['snippet']}\n**Link:** {article['link']}"
        await post_to_telegram(bot, message)
        history.append([article["title"], article["link"], datetime.now().timestamp()])

    save_history(history)

if __name__ == "__main__":
    print(f"Starting scrape at {datetime.now()}")
    asyncio.run(main())
