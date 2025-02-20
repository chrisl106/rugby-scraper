import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
from datetime import datetime
from config import TELEGRAM_TOKEN, CHANNEL_ID, TARGET_URLS, SPOILER_TERMS
import json
from fuzzywuzzy import fuzz
from dateutil.parser import parse
import time  # For cooldown

async def post_to_telegram(bot, message):
    """Send a message to the Telegram channel with retry logic."""
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=message, disable_web_page_preview=False, parse_mode="Markdown")
        print(f"Posted at {datetime.now()}: {message[:50]}...")
    except Exception as e:
        print(f"Telegram error: {e}")
        await asyncio.sleep(1)  # Brief retry delay if error

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
        if fuzz.token_sort_ratio(new_title, old_title) >= threshold:
            return True
    return False

def try_parse_date(text):
    """Attempt to parse a date from text (e.g., article metadata)."""
    try:
        if "datetime" in text:
            return parse(text.split("datetime")[1].strip('"\''))
        return parse(text, fuzzy=True)
    except (ValueError, IndexError):
        return datetime.now()  # Default to now if no date found

def scrape_rugby_news():
    """Scrape up to 5 most recent headlines, snippets, and links from each rugby news site, skipping duplicates and spoilers."""
    articles = []
    seen = set()
    history = load_history()
    headers = {"User-Agent": "Mozilla/5.0"}  # Mimic browser to avoid blocks

    for url in TARGET_URLS:
        site_articles = []  # Articles from this site only
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            news_selectors = [
                "article",
                ".news-article",
                ".news-item",
                ".post",
                ".article-content",
                "div.entry-content h2",
                ".blog-post h2",
            ]
            
            for selector in news_selectors:
                news_items = soup.select(selector)
                for item in news_items:
                    title_elem = item.find("h1") or item.find("h2") or item.find("h3")
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    link_elem = item.find("a")
                    link = link_elem["href"] if link_elem and "href" in link_elem.attrs else url
                    
                    snippet_elem = item.find("p") or item.find("div", class_=["excerpt", "summary", "description"])
                    snippet = snippet_elem.get_text(strip=True)[:150] + "..." if snippet_elem else ""
                    
                    if not title or not link:
                        continue
                    
                    # Try to find publication date for sorting
                    date_elem = item.find("time") or item.find("span", class_=["date", "published"])
                    pub_date = try_parse_date(date_elem.get("datetime", "") if date_elem else title)
                    
                    if is_spoiler_free(title + " " + snippet):
                        site_articles.append({
                            "title": title,
                            "snippet": snippet,
                            "link": link,
                            "date": pub_date,
                            "site": url  # Track site for per-site limit
                        })
        
        except Exception as e:
            print(f"Error scraping {url}: {e}")
        
        # Sort articles from this site by date (most recent first)
        site_articles.sort(key=lambda x: x["date"], reverse=True)
        
        # Take up to 5 most recent, non-duplicate articles from this site
        for article in site_articles[:5]:
            article_key = f"{article['title']}|{article['link']}"
            if article_key not in seen and not is_duplicate(article['title'], article['link'], history):
                articles.append(article)
                seen.add(article_key)
    
    return articles  # Return all valid articles (up to 5/site)

async def main():
    """Main function to scrape and post hourly with cooldown."""
    bot = telegram.Bot(TELEGRAM_TOKEN)
    articles = scrape_rugby_news()
    history = load_history()

    for article in articles:
        # Format: bold headline, plain snippet, plain link, with escaping for Markdown
        message = f"*{article['title'].replace('*', '\\*').replace('_', '\\_')}*\n{article['snippet']}\n{article['link']}"
        await post_to_telegram(bot, message)
        time.sleep(0.5)  # 0.5-second cooldown between posts
        history.append([article["title"], article["link"], datetime.now().timestamp()])

    save_history(history)

if __name__ == "__main__":
    print(f"Starting scrape at {datetime.now()}")
    asyncio.run(main())
