#!/usr/bin/env python3
"""
MR. ROBOT — Xəbər Botu v3 (GitHub Actions)
Azərbaycan mənbələri: yalnız AZ haqqında tech xəbərlər
"""

import logging, asyncio, feedparser, json, os, hashlib, re
from datetime import datetime
from deep_translator import GoogleTranslator
from telegram import Bot
from telegram.constants import ParseMode

BOT_TOKEN  = os.environ.get("BOT_TOKEN", "7384331973:AAHtjjNtG5p6hQbnZRoi9eyyja_nB43QLgE")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@mr_robot_az")
SEEN_FILE  = "seen_articles.json"
MAX_PER_RUN = 8

# ════════════════════════════════════════════
#  AZƏRBAYCAN MƏNBƏLƏRİ ÜÇÜN FİLTRLƏR
# ════════════════════════════════════════════

# Mütləq bu sözlərdən biri olmalıdır (AZ haqqında olduğunu bildirir)
AZ_REQUIRED = [
    "azərbaycan", "azerbaijan", "azerbaycan", "baku", "bakı",
    "azərbaycanda", "azərbaycanlı", "azərbaycana", "azərbaycandan",
    "bakıda", "bakıya", "asan xidmət", "e-gov", "azərconnect",
    "azercell", "bakcell", "nar mobile", "ibar", "kapital bank",
    "pasha", "atb", "teknoparka", "texnopark", "it park baku",
    "ada university", "bsu", "banker.az", "aztelecom"
]

# Bu sözlər varsa — keç (siyasət, xəbər deyil)
AZ_BLOCK = [
    "prezident", "nazir", "parlament", "seçki", "hökumət",
    "müharibə", "ordu", "hərbi", "diplomatik", "cinayət",
    "qəza", "yanğın", "zəlzələ", "döyüş", "həbs", "məhkəmə",
    "idman", "futbol", "basketbol", "voleybol", "neftçi",
    "neft qiymət", "valyuta", "dollar", "manat məzənnə",
    "hava", "proqnoz", "iqlim hadisə"
]

# Tech açar sözlər — ən azı biri olmalıdır
AZ_TECH = [
    "texnologiya", "technology", "tech", "it ", " it,", "proqram",
    "kompüter", "computer", "internet", "rəqəmsal", "digital",
    "startup", "süni intellekt", "artificial intelligence", "ai ",
    "robot", "innovasiya", "innovation", "software", "hardware",
    "kibər", "cyber", "mobil", "mobile", "gadget", "elektron",
    "electronic", "microsoft", "google", "apple", "samsung",
    "5g", "blockchain", "cloud", "data", "proqramlaşdırma",
    "coding", "developer", "app ", "tətbiq", "platforma",
    "hackathon", "texnopark", "it park", "fintech", "e-commerce",
    "rəqəmləşmə", "digitalization", "e-government", "elektron"
]

def az_is_ok(title: str, summary: str) -> bool:
    """Azərbaycan mənbəsi üçün 3 şərt:
    1. AZ haqqında olmalıdır
    2. Blok söz yoxdur
    3. Tech mövzusundadır
    """
    text = (title + " " + summary).lower()

    # Şərt 1: Azərbaycan haqqındadır?
    has_az = any(kw in text for kw in AZ_REQUIRED)
    if not has_az:
        return False

    # Şərt 2: Blok söz yoxdur?
    for kw in AZ_BLOCK:
        if kw in text:
            return False

    # Şərt 3: Tech mövzusundadır?
    has_tech = any(kw in text for kw in AZ_TECH)
    return has_tech

# ════════════════════════════════════════════
#  RSS MƏNBƏLƏR
# ════════════════════════════════════════════
RSS_FEEDS = [
    # 🤖 SÜNİ İNTELLEKT
    {"url": "https://techcrunch.com/category/artificial-intelligence/feed/",
     "emoji": "🤖", "tag": "SüniIntellekt", "az_source": False},
    {"url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
     "emoji": "🤖", "tag": "SüniIntellekt", "az_source": False},
    {"url": "https://venturebeat.com/category/ai/feed/",
     "emoji": "🤖", "tag": "SüniIntellekt", "az_source": False},

    # 💻 TEXNOLOGİYA
    {"url": "https://feeds.feedburner.com/TechCrunch",
     "emoji": "💻", "tag": "Texnologiya", "az_source": False},
    {"url": "https://www.theverge.com/rss/index.xml",
     "emoji": "💻", "tag": "Texnologiya", "az_source": False},
    {"url": "https://arstechnica.com/feed/",
     "emoji": "💻", "tag": "Texnologiya", "az_source": False},
    {"url": "https://www.wired.com/feed/rss",
     "emoji": "💻", "tag": "Texnologiya", "az_source": False},

    # 🎮 OYUNLAR
    {"url": "https://feeds.ign.com/ign/all",
     "emoji": "🎮", "tag": "Oyunlar", "az_source": False},
    {"url": "https://www.eurogamer.net/?format=rss",
     "emoji": "🎮", "tag": "Oyunlar", "az_source": False},
    {"url": "https://kotaku.com/rss",
     "emoji": "🎮", "tag": "Oyunlar", "az_source": False},

    # 🛡️ KİBERTƏHLÜKƏSİZLİK
    {"url": "https://feeds.feedburner.com/TheHackersNews",
     "emoji": "🛡️", "tag": "Kibertəhlükəsizlik", "az_source": False},
    {"url": "https://www.bleepingcomputer.com/feed/",
     "emoji": "🛡️", "tag": "Kibertəhlükəsizlik", "az_source": False},
    {"url": "https://krebsonsecurity.com/feed/",
     "emoji": "🛡️", "tag": "Kibertəhlükəsizlik", "az_source": False},

    # 📚 IT TƏHSİL
    {"url": "https://www.freecodecamp.org/news/rss/",
     "emoji": "📚", "tag": "ITTəhsil", "az_source": False},
    {"url": "https://dev.to/feed",
     "emoji": "📚", "tag": "ITTəhsil", "az_source": False},
    {"url": "https://hackernoon.com/feed",
     "emoji": "📚", "tag": "ITTəhsil", "az_source": False},

    # 🇦🇿 AZƏRBAYCAN TECH — 3 FİLTR İLƏ
    {"url": "https://caliber.az/rss.xml",
     "emoji": "🇦🇿", "tag": "AzərbaycanTech", "az_source": True},
    {"url": "https://report.az/rss/",
     "emoji": "🇦🇿", "tag": "AzərbaycanTech", "az_source": True},
    {"url": "https://www.trend.az/it/rss.xml",
     "emoji": "🇦🇿", "tag": "AzərbaycanTech", "az_source": True},
    {"url": "https://banker.az/feed/",
     "emoji": "🇦🇿", "tag": "AzərbaycanTech", "az_source": True},
]

# ════════════════════════════════════════════
#  YARDIMÇI
# ════════════════════════════════════════════
def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE) as f: return set(json.load(f))
        except: pass
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen)[-5000:], f)

def make_id(entry):
    return hashlib.md5((entry.get("link","") or entry.get("title","")).encode()).hexdigest()

def clean(text):
    text = re.sub(r'<[^>]+>', '', str(text))
    for e,r in [('&amp;','&'),('&lt;','<'),('&gt;','>'),('&#39;',"'"),('&nbsp;',' ')]:
        text = text.replace(e, r)
    return re.sub(r'\s+', ' ', text).strip()

def translate(text, limit=800):
    if not text: return ""
    try:
        return GoogleTranslator(source='auto', target='az').translate(text[:limit]) or text
    except: return text

def get_summary(entry):
    for f in ["summary","description","content"]:
        v = entry.get(f,"")
        if isinstance(v, list): v = v[0].get("value","") if v else ""
        if v:
            s = clean(v)
            return (s[:600]+"…") if len(s)>600 else s
    return ""

def format_post(entry, feed):
    title   = clean(entry.get("title",""))
    link    = entry.get("link","")
    summary = get_summary(entry)
    t = translate(title, 400)
    b = translate(summary, 600) if summary else ""
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    msg  = f"{feed['emoji']} <b>#{feed['tag']}</b>\n\n<b>{t}</b>\n"
    if b: msg += f"\n{b}\n"
    msg += f"\n🔗 <a href='{link}'>Ətraflı oxu →</a>"
    msg += f"\n\n<i>🕐 {now} | @mr_robot_az</i>"
    return msg

# ════════════════════════════════════════════
#  ƏSAS
# ════════════════════════════════════════════
async def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN tapılmadı!"); return

    bot    = Bot(token=BOT_TOKEN)
    seen   = load_seen()
    posted = 0

    for feed_info in RSS_FEEDS:
        if posted >= MAX_PER_RUN: break
        try:
            feed    = feedparser.parse(feed_info["url"])
            entries = list(reversed(feed.entries[:5]))

            for entry in entries:
                if posted >= MAX_PER_RUN: break
                aid = make_id(entry)
                if aid in seen: continue
                seen.add(aid)

                # Azərbaycan mənbəsi — 3 filtri keç
                if feed_info.get("az_source"):
                    title   = clean(entry.get("title",""))
                    summary = get_summary(entry)
                    if not az_is_ok(title, summary):
                        logging.info(f"⏭️  Filtr: {title[:60]}")
                        continue

                try:
                    await bot.send_message(
                        chat_id=CHANNEL_ID,
                        text=format_post(entry, feed_info),
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=False
                    )
                    posted += 1
                    logging.info(f"✅ [{feed_info['tag']}] {entry.get('title','?')[:60]}")
                    await asyncio.sleep(4)
                except Exception as e:
                    logging.error(f"Send: {e}"); await asyncio.sleep(5)

        except Exception as e:
            logging.error(f"RSS: {e}")

    save_seen(seen)
    print(f"✅ {posted} yeni xəbər göndərildi.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
    asyncio.run(main())
