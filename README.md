Rugby News Scraper Setup Guide
-----------------------------

Scrapes rugby news hourly, posts to Telegram group, skips match results/duplicates. Runs in a virtual environment on Lightsail.

### Server Recommendation
- **AWS Lightsail:** $3.50/month (1 GB RAM, 1 vCPU, 20 GB SSD, 1 TB bandwidth).

### Prerequisites
- Python 3.8+ (Ubuntu 22.04+)
- Telegram bot and supergroup (bot must be admin)
- Git installed

### Steps
1. **Set Up Lightsail Instance**
   - Launch Ubuntu 22.04 on Lightsail ($3.50/month).
   - SSH in: `ssh ubuntu@your-instance-ip`

2. **Clone the Repo**
   - Install Git: `sudo apt update && sudo apt install git`
   - Clone: `git clone https://github.com/chrisl106/rugby-scraper.git`
   - Move in: `cd rugby-scraper`

3. **Set Up Virtual Environment**
   - Install venv: `sudo apt install python3-venv`
   - Create venv: `python3 -m venv venv`
   - Activate: `source venv/bin/activate`

4. **Install Dependencies**
   - Run: `pip install -r requirements.txt` (in venv)

5. **Set Up Telegram Bot**
   - Create bot with @BotFather: `/newbot`, name it (e.g., "RugbyNewsBot"), get token.
   - For private supergroups: Get group invite link (Group Info > Invite Link), send to bot in Telegram to join.
   - Add bot to group: Group Info > Add Member > Search bot > Add (or use invite link).
   - Make admin: Manage > Administrators > Bot > Enable "Post Messages" (confirm "Delete Messages" is on).

6. **Get Group Chat ID**
   - Add @RawDataBot to group, send "test".
   - Copy exact ID (e.g., "-1002338197095").

7. **Configure the Script**
   - Edit `config.py`:
     - `TELEGRAM_TOKEN = "your-bot-token-here"`
     - `CHANNEL_ID = "-1002338197095"` (exact ID from step 6)
     - Add URLs to `TARGET_URLS` if desired.
     - Adjust `SPOILER_TERMS` if needed.

8. **Test Locally**
   - Run: `python rugby_news_scraper.py` (in venv)
   - Check group for posts. Posts format as:
     - `*Headline*` (bold, no label)
     - `Snippet...` (plain, no label)
     - `Link` (plain, no label)
   - Up to 5 most recent articles per site, no duplicates, no spoilers.
   - If “Telegram timed out,” adjust cooldown in `main()` (e.g., `time.sleep(1.0)`).
   - If scraping pulls menus, update `rugby_news_scraper.py`:
     - Inspect site HTML (e.g., `all.rugby/news/`) with browser DevTools.
     - Adjust `news_selectors` in `scrape_rugby_news()` to target news (e.g., `.news-story`, `article`).
   - If dates don’t sort, tweak `try_parse_date()` with site-specific date patterns.

9. **Schedule Hourly Runs**
   - Open crontab: `crontab -e`
   - Add: `0 * * * * /home/ubuntu/rugby-scraper/venv/bin/python /home/ubuntu/rugby-scraper/rugby_news_scraper.py`

10. **Deactivate**
    - Run: `deactivate`

### Troubleshooting
- **"Chat not found" (400):**
  - Ensure `CHANNEL_ID` matches exact ID from @RawDataBot.
  - Verify bot is in group with "Post Messages" (check "Delete Messages").
  - For private groups, re-invite bot via group invite link.
  - Test: `curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" -d "chat_id=-1002338197095&text=Test"`
- **"Unauthorized" (401):**
  - Check `TELEGRAM_TOKEN` is current (revoke/recreate via @BotFather).
- **"Telegram timed out":**
  - Increase cooldown in `main()` (e.g., `time.sleep(1.0)`).

### Notes
- Posts capped at 5 per site/hour—adjust in `scrape_rugby_news()`.
- Duplicates filtered across all sites, spoilers skipped.
- History in `posted.json` capped at 7 days.
