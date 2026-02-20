#!/usr/bin/env python3
"""
MR. ROBOT — Xəbər Botu (GitHub Actions versiyası)
Token ve Kanal ID GitHub Secrets-den oxunur.
"""

import logging, asyncio, feedparser, json, os, hashlib, re
from datetime import datetime
from deep_translator import GoogleTranslator
from telegram import Bot
from telegram.constants import ParseMode

BOT_TOKEN  = os.environ.get("BOT_TOKEN", "7384331973:AAHtjjNtG5p6hQbnZRoi9eyyja_nB43QLgE")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@mr_robot_az")
SEEN_FILE  = "seen_articles.json"

RSS_FEEDS = [
    {"url": "https://techcrunch.com/category/artificial-intelligence/feed/", "emoji": "🤖", "tag": "SüniIntellekt"},
    {"url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml", "emoji": "🤖", "tag": "SüniIntellekt"},
    {"url": "https://venturebeat.com/category/ai/feed/", "emoji": "🤖", "tag": "SüniIntellekt"},
    {"url": "https://feeds.feedburner.com/TechCrunch", "emoji": "💻", "tag": "Texnologiya"},
    {"url": "https://www.theverge.com/rss/index.xml", "emoji": "💻", "tag": "Texnologiya"},
    {"url": "https://arstechnica.com/feed/", "emoji": "💻", "tag": "Texnologiya"},
    {"url": "https://www.wired.com/feed/rss", "emoji": "💻", "tag": "Texnologiya"},
    {"url": "https://feeds.ign.com/ign/all", "emoji": "🎮", "tag": "Oyunlar"},
    {"url": "https://www.eurogamer.net/?format=rss", "emoji": "🎮", "tag": "Oyunlar"},
    {"url": "https://kotaku.com/rss", "emoji": "🎮", "tag": "Oyunlar"},
    {"url": "https://feeds.feedburner.com/TheHackersNews", "emoji": "🛡️", "tag": "Kibertəhlükəsizlik"},
    {"url": "https://www.bleepingcomputer.com/feed/", "emoji": "🛡️", "tag": "Kibertəhlükəsizlik"},
    {"url": "https://krebsonsecurity.com/feed/", "emoji": "🛡️", "tag": "Kibertəhlükəsizlik"},
    {"url": "https://caliber.az/rss.xml", "emoji": "🇦🇿", "tag": "Azərbaycan"},
    {"url": "https://report.az/rss/", "emoji": "🇦🇿", "tag": "Azərbaycan"},
    {"url": "https://www.trend.az/rss/", "emoji": "🇦🇿", "tag": "Azərbaycan"},
]

def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE) as f: return set(json.load(f))
        except: pass
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f: json.dump(list(seen)[-5000:], f)

def make_id(entry):
    return hashlib.md5((entry.get("link","") or entry.get("title","")).encode()).hexdigest()

def clean(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&amp;','&',text); text = re.sub(r'&lt;','<',text)
    text = re.sub(r'&gt;','>',text);  text = re.sub(r'&#39;',"'",text)
    return re.sub(r'\s+',' ',text).strip()

def translate(text, limit=800):
    if not text: return ""
    try: return GoogleTranslator(source='auto', target='az').translate(text[:limit]) or text
    except: return text

def fmt(entry, feed):
    title = clean(entry.get("title",""))
    link  = entry.get("link","")
    body  = ""
    for f in ["summary","description"]:
        v = entry.get(f,"")
        if isinstance(v, list): v = v[0].get("value","") if v else ""
        if v: body = clean(v); break
    body = body[:700]+"…" if len(body)>700 else body
    t = translate(title, 400)
    b = translate(body, 700) if body else ""
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    msg = f"{feed['emoji']} <b>#{feed['tag']}</b>\n\n<b>{t}</b>\n"
    if b: msg += f"\n{b}\n"
    msg += f"\n🔗 <a href='{link}'>Ətraflı oxu →</a>"
    msg += f"\n\n<i>🕐 {now} | @mr_robot_az</i>"
    return msg

async def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN yoxdur!"); return
    bot = Bot(token=BOT_TOKEN)
    seen = load_seen()
    posted = 0
    for feed_info in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in reversed(feed.entries[:3]):
                aid = make_id(entry)
                if aid in seen: continue
                seen.add(aid)
                try:
                    await bot.send_message(chat_id=CHANNEL_ID, text=fmt(entry, feed_info),
                        parse_mode=ParseMode.HTML, disable_web_page_preview=False)
                    posted += 1
                    await asyncio.sleep(4)
                except Exception as e:
                    logging.error(f"Send error: {e}"); await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"RSS error: {e}")
    save_seen(seen)
    print(f"✅ {posted} yeni xəbər göndərildi.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
