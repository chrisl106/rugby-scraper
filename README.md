# rugby-scraper

Rugby News Scraper Setup Guide
-----------------------------

This script scrapes rugby news articles hourly and posts them to a Telegram channel, skipping match results and duplicates. Deploy from this GitHub repo.

### Server Recommendation
- **AWS Lightsail:** $3.50/month plan (1 GB RAM, 1 vCPU, 20 GB SSD, 1 TB bandwidth).
  - Light workload: ~10-15 HTTP requests/hour, <100 MB RAM, <1 MB storage.
  - Perfect for hourly cron with 99.9% uptime.

### Prerequisites
- Python 3.8 or higher
- A Telegram bot and channel
- Git installed on the server

### Steps
1. **Set Up Lightsail Instance**
   - Launch an Ubuntu 20.04 instance on Lightsail ($3.50/month).
   - SSH in: `ssh ubuntu@your-instance-ip`

2. **Clone the Repo**
   - Install Git: `sudo apt update && sudo apt install git`
   - Clone: `git clone https://github.com/yourusername/your-repo-name.git`
   - Move in: `cd your-repo-name`

3. **Install Dependencies**
   - Install Python tools: `sudo apt install python3-pip`
   - Run: `pip3 install -r requirements.txt`

4. **Set Up Telegram Bot**
   - Chat with @BotFather on Telegram, create a bot with `/newbot`.
   - Copy the bot token (e.g., "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11").
   - Add the bot as an admin to your channel.

5. **Configure the Script**
   - Edit `config.py`:
     - Replace `TELEGRAM_TOKEN` with your bot token.
     - Replace `CHANNEL_ID` with your channel ID (e.g., "@RugbyNewsChannel").
     - Add more URLs to `TARGET_URLS` if desired.
     - Adjust `SPOILER_TERMS` if needed.

6. **Test Locally**
   - Run: `python3 rugby_news_scraper.py`
   - Check your Telegram channel for posts.

7. **Schedule Hourly Runs**
   - Open crontab: `crontab -e`
   - Add: `0 * * * * /usr/bin/python3 /home/ubuntu/your-repo-name/rugby_news_scraper.py`
   - Save and exit—runs hourly.

### Notes
- Posts capped at 5/hour—adjust in `main()` if needed.
- Duplicates filtered by URL and fuzzy title matching (85% similarity).
- History in `posted.json` capped at 7 days.
- Tweak `is_duplicate()` threshold (default 85) if needed.
- Update repo with `git pull` if changes are pushed later.

Deploy on Lightsail from this repo, and your rugby news is live!
