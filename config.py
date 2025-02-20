# Configuration for rugby news scraper

# Telegram bot token from BotFather
TELEGRAM_TOKEN = "your-bot-token-here"

# Your Telegram channel ID (e.g., @RugbyNewsChannel)
CHANNEL_ID = "your-channel-id-here"

# List of rugby news sites to scrape
TARGET_URLS = [
    "https://all.rugby/news/",
    "https://www.rugbypass.com/news/",
    "https://www.bbc.com/sport/rugby-union",
    "https://www.rugby365.com/news/",
    "https://www.planetrugby.com/news",
    # Add more sites as needed
]

# Keywords to filter out match results or spoilers
SPOILER_TERMS = [
    "score", "result", "beat", "defeated", "win", "loss", "try count",
    "tries", "conversion", r"\d+\-\d+"  # e.g., "20-15"
]
