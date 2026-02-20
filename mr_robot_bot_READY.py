#!/usr/bin/env python3
"""
MR. ROBOT — Telegram Bot v2
Dillər / Языки / Languages: AZ | RU | EN
Quraşdırma / Установка:
  pip install python-telegram-bot==20.7
  python mr_robot_bot_v2.py
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler
)

BOT_TOKEN = "7978877071:AAEUDFzDiwPQ93JvI-TCOHVXIAW-KvADd8o"
ADMIN_CHAT_ID = 2146354201
CONTACT = "@mr.robot.az"

PRICES = {
    "diag":    {"az": "Diaqnostika (NB/PC)",        "ru": "Диагностика (NB/ПК)",         "en": "Diagnostics (NB/PC)",       "price": "20 ₼"},
    "clean":   {"az": "Təmizlik + termopasta",       "ru": "Чистка + термопаста",          "en": "Cleaning + thermal paste",  "price": "30 ₼"},
    "windows": {"az": "Windows quraşdırma",          "ru": "Установка Windows",            "en": "Windows installation",      "price": "25 ₼"},
    "screen":  {"az": "Noutbuk ekranı dəyişimi",    "ru": "Замена экрана ноутбука",       "en": "Laptop screen replacement", "price": "80 ₼+"},
    "virus":   {"az": "Virus təmizliyi",             "ru": "Удаление вирусов",             "en": "Virus removal",             "price": "20 ₼"},
    "data":    {"az": "Məlumat bərpası",             "ru": "Восстановление данных",        "en": "Data recovery",             "price": "40 ₼"},
    "upgrade": {"az": "RAM / SSD yüksəltmə",        "ru": "Апгрейд RAM / SSD",            "en": "RAM / SSD upgrade",         "price": "15 ₼ (hissə ayrıca)"},
    "remote":  {"az": "Uzaqdan yardım (TeamViewer)","ru": "Удалённая помощь (TeamViewer)","en": "Remote help (TeamViewer)",  "price": "15 ₼"},
}

TEXTS = {
    "choose_device": {
        "az": "💻 Hansı cihazınızda problem var?",
        "ru": "💻 С каким устройством проблема?",
        "en": "💻 What device has the problem?",
    },
    "choose_problem": {
        "az": "🔧 Problem nədir?",
        "ru": "🔧 В чём проблема?",
        "en": "🔧 What's the problem?",
    },
    "choose_service": {
        "az": "🛠️ Hansı xidməti seçirsiniz?",
        "ru": "🛠️ Какую услугу выбираете?",
        "en": "🛠️ Which service do you need?",
    },
    "visit_type": {
        "az": "📍 Necə işləmək istərdiniz?",
        "ru": "📍 Как хотите работать?",
        "en": "📍 How would you like to proceed?",
    },
    "confirm": {
        "az": "✅ <b>Sifariş qəbul edildi!</b>\n\n🤖 Ustamız tezliklə sizinlə əlaqə saxlayacaq.\n📲 Birbaşa əlaqə: <b>{contact}</b>\n\n<i>Adətən 15-30 dəqiqə ərzində cavab veririk.</i>",
        "ru": "✅ <b>Заявка принята!</b>\n\n🤖 Наш мастер свяжется с вами в ближайшее время.\n📲 Прямой контакт: <b>{contact}</b>\n\n<i>Обычно отвечаем в течение 15-30 минут.</i>",
        "en": "✅ <b>Request received!</b>\n\n🤖 Our technician will contact you shortly.\n📲 Direct contact: <b>{contact}</b>\n\n<i>We usually reply within 15-30 minutes.</i>",
    },
    "price_list": {
        "az": "💰 <b>Qiymət Siyahısı — MR. ROBOT</b>\n\n",
        "ru": "💰 <b>Прайс-лист — MR. ROBOT</b>\n\n",
        "en": "💰 <b>Price List — MR. ROBOT</b>\n\n",
    },
}

LANG, DEVICE, PROBLEM, SERVICE, VISIT = range(5)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lang_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇦🇿 Azərbaycanca", callback_data="lang_az"),
        InlineKeyboardButton("🇷🇺 Русский",       callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English",       callback_data="lang_en"),
    ]])

def device_keyboard(lang):
    d = {
        "az": [("💻 Noutbuk", "dev_nb"), ("🖥️ PC / Masa üstü", "dev_pc")],
        "ru": [("💻 Ноутбук", "dev_nb"), ("🖥️ ПК / Десктоп",   "dev_pc")],
        "en": [("💻 Laptop",  "dev_nb"), ("🖥️ Desktop PC",     "dev_pc")],
    }
    return InlineKeyboardMarkup([[InlineKeyboardButton(l, callback_data=c)] for l, c in d[lang]])

def problem_keyboard(lang):
    p = {
        "az": [
            ("🐌 Yavaş işləyir",               "prob_slow"),
            ("🔥 Qızır / söndürülür",           "prob_heat"),
            ("💥 Ekran xarabdır",               "prob_screen"),
            ("🔇 Səs işləmir",                  "prob_sound"),
            ("🦠 Virus / zərərli proqram",       "prob_virus"),
            ("💾 Windows problemi",              "prob_win"),
            ("💧 Su düşüb",                     "prob_water"),
            ("⚡ Açılmır / işə düşmür",         "prob_nostart"),
            ("📶 İnternet / Wi-Fi problemi",     "prob_net"),
            ("❓ Digər problem",                 "prob_other"),
        ],
        "ru": [
            ("🐌 Работает медленно",             "prob_slow"),
            ("🔥 Перегревается / выключается",   "prob_heat"),
            ("💥 Сломан экран",                  "prob_screen"),
            ("🔇 Не работает звук",              "prob_sound"),
            ("🦠 Вирус / вредоносное ПО",        "prob_virus"),
            ("💾 Проблема с Windows",            "prob_win"),
            ("💧 Попала вода",                   "prob_water"),
            ("⚡ Не включается",                 "prob_nostart"),
            ("📶 Проблема с интернетом / Wi-Fi", "prob_net"),
            ("❓ Другая проблема",               "prob_other"),
        ],
        "en": [
            ("🐌 Running slow",                  "prob_slow"),
            ("🔥 Overheating / shutting off",    "prob_heat"),
            ("💥 Screen broken",                 "prob_screen"),
            ("🔇 No sound",                      "prob_sound"),
            ("🦠 Virus / malware",               "prob_virus"),
            ("💾 Windows issue",                 "prob_win"),
            ("💧 Water damage",                  "prob_water"),
            ("⚡ Won't turn on",                 "prob_nostart"),
            ("📶 Internet / Wi-Fi issue",        "prob_net"),
            ("❓ Other problem",                 "prob_other"),
        ],
    }
    return InlineKeyboardMarkup([[InlineKeyboardButton(l, callback_data=c)] for l, c in p[lang]])

def service_keyboard(lang, problem):
    mapping = {
        "prob_slow":    ["clean", "upgrade", "windows", "virus"],
        "prob_heat":    ["clean", "diag"],
        "prob_screen":  ["screen", "diag"],
        "prob_sound":   ["diag", "windows"],
        "prob_virus":   ["virus", "windows"],
        "prob_win":     ["windows", "virus", "diag"],
        "prob_water":   ["diag"],
        "prob_nostart": ["diag"],
        "prob_net":     ["diag", "windows", "remote"],
        "prob_other":   ["diag", "remote"],
    }
    keys = mapping.get(problem, ["diag", "remote"])
    rows = []
    for key in keys:
        p = PRICES.get(key, {})
        label = f"{p.get(lang, key)} — {p.get('price','?')}"
        rows.append([InlineKeyboardButton(label, callback_data=f"svc_{key}")])
    return InlineKeyboardMarkup(rows)

def visit_keyboard(lang):
    v = {
        "az": [("🏠 Evinizə / ofisinizə gəlirik", "visit_home"), ("🔧 Özüm gətirəcəyəm", "visit_bring")],
        "ru": [("🏠 Выезд к вам домой / в офис",  "visit_home"), ("🔧 Привезу сам",       "visit_bring")],
        "en": [("🏠 Come to my home / office",     "visit_home"), ("🔧 I'll bring it",     "visit_bring")],
    }
    return InlineKeyboardMarkup([[InlineKeyboardButton(l, callback_data=c)] for l, c in v[lang]])

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    msg = (
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖  <b>MR. ROBOT — Tech Support</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🇦🇿 Dil seçin\n"
        "🇷🇺 Выберите язык\n"
        "🇬🇧 Choose language"
    )
    await update.message.reply_html(msg, reply_markup=lang_keyboard())
    return LANG

async def set_language(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    ctx.user_data["lang"] = lang
    await query.edit_message_text(TEXTS["choose_device"][lang], reply_markup=device_keyboard(lang), parse_mode="HTML")
    return DEVICE

async def set_device(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = ctx.user_data["lang"]
    ctx.user_data["device"] = query.data
    await query.edit_message_text(TEXTS["choose_problem"][lang], reply_markup=problem_keyboard(lang), parse_mode="HTML")
    return PROBLEM

async def set_problem(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = ctx.user_data["lang"]
    ctx.user_data["problem"] = query.data
    await query.edit_message_text(TEXTS["choose_service"][lang], reply_markup=service_keyboard(lang, query.data), parse_mode="HTML")
    return SERVICE

async def set_service(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = ctx.user_data["lang"]
    key = query.data.replace("svc_", "")
    p = PRICES.get(key, {})
    ctx.user_data["service_name"] = p.get(lang, key)
    ctx.user_data["service_price"] = p.get("price", "?")

    if key == "remote":
        ctx.user_data["visit"] = "🌐 Remote / Uzaqdan"
        await _finalize(query, ctx)
        return ConversationHandler.END

    await query.edit_message_text(TEXTS["visit_type"][lang], reply_markup=visit_keyboard(lang), parse_mode="HTML")
    return VISIT

async def set_visit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = ctx.user_data["lang"]
    labels = {
        "az": {"visit_home": "🏠 Evinizə gəlirik", "visit_bring": "🔧 Özüm gətirəcəyəm"},
        "ru": {"visit_home": "🏠 Выезд к вам",      "visit_bring": "🔧 Привезу сам"},
        "en": {"visit_home": "🏠 Come to me",        "visit_bring": "🔧 I'll bring it"},
    }
    ctx.user_data["visit"] = labels[lang].get(query.data, query.data)
    await _finalize(query, ctx)
    return ConversationHandler.END

async def _finalize(query, ctx):
    lang = ctx.user_data["lang"]
    user = query.from_user
    dev_map = {
        "dev_nb": {"az": "💻 Noutbuk", "ru": "💻 Ноутбук", "en": "💻 Laptop"},
        "dev_pc": {"az": "🖥️ PC",      "ru": "🖥️ ПК",      "en": "🖥️ PC"},
    }
    device_name = dev_map.get(ctx.user_data.get("device",""), {}).get(lang, "?")

    summary = (
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 <b>YENİ SİFARİŞ / НОВАЯ ЗАЯВКА</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 {user.full_name} (@{user.username or '—'})\n"
        f"🌐 Dil: {lang.upper()}\n"
        f"💻 Cihaz: {device_name}\n"
        f"🛠️ Xidmət: {ctx.user_data.get('service_name','?')}\n"
        f"💰 Qiymət: {ctx.user_data.get('service_price','?')}\n"
        f"📍 Üsul: {ctx.user_data.get('visit','?')}\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )
    try:
        await ctx.bot.send_message(ADMIN_CHAT_ID, summary, parse_mode="HTML")
    except Exception as e:
        logger.warning(f"Admin notification failed: {e}")

    await query.edit_message_text(TEXTS["confirm"][lang].format(contact=CONTACT), parse_mode="HTML")

async def price_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = ctx.user_data.get("lang", "az")
    text = TEXTS["price_list"][lang]
    for key, p in PRICES.items():
        text += f"• <b>{p.get(lang, key)}</b> — {p.get('price','?')}\n"
    text += f"\n📲 {CONTACT}"
    await update.message.reply_html(text)

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Ləğv edildi / Отменено / Cancelled")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG:    [CallbackQueryHandler(set_language, pattern="^lang_")],
            DEVICE:  [CallbackQueryHandler(set_device,   pattern="^dev_")],
            PROBLEM: [CallbackQueryHandler(set_problem,  pattern="^prob_")],
            SERVICE: [CallbackQueryHandler(set_service,  pattern="^svc_")],
            VISIT:   [CallbackQueryHandler(set_visit,    pattern="^visit_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    app.add_handler(CommandHandler("prices", price_list))
    print("🤖 MR. ROBOT Bot v2 işə düşdü / запущен / started...")
    app.run_polling()

if __name__ == "__main__":
    main()
