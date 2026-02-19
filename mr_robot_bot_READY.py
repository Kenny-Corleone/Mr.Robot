#!/usr/bin/env python3
"""
MR. ROBOT — Telegram Bot
Dillər / Языки / Languages: AZ | RU | EN
Quraşdırma / Установка:
  pip install python-telegram-bot==20.7
  python mr_robot_bot.py
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ════════════════════════════════════════════
#  KONFİQURASİYA / КОНФИГУРАЦИЯ / CONFIG
# ════════════════════════════════════════════
BOT_TOKEN = "7978877071:AAE-68LSRPENLaLcuxNny_MTaeDGBDMLBeA"   # @BotFather-dən aldığın token
ADMIN_CHAT_ID = 2146354201            # Sənin Telegram ID-n (t.me/userinfobot-dan öyrən)
CONTACT = "@mr.robot.az"            # WhatsApp / Telegram

# ════════════════════════════════════════════
#  QİYMƏTLƏR / ЦЕНЫ / PRICES  (₼)
# ════════════════════════════════════════════
PRICES = {
    "diag_nb":    {"az": "Noutbuk diaqnostikası",    "ru": "Диагностика ноутбука",     "en": "Laptop diagnostics",     "price": "PULSUZ / БЕСПЛАТНО / FREE"},
    "diag_pc":    {"az": "PC diaqnostikası",          "ru": "Диагностика ПК",           "en": "PC diagnostics",         "price": "PULSUZ / БЕСПЛАТНО / FREE"},
    "clean":      {"az": "Təmizlik + termopasta",      "ru": "Чистка + термопаста",      "en": "Cleaning + thermal paste","price": "30 ₼"},
    "windows":    {"az": "Windows quraşdırma",         "ru": "Установка Windows",        "en": "Windows installation",   "price": "25 ₼"},
    "screen_nb":  {"az": "Noutbuk ekranı dəyişimi",   "ru": "Замена экрана ноутбука",   "en": "Laptop screen replace",  "price": "80 ₼+"},
    "screen_ph":  {"az": "Smartfon ekranı dəyişimi",  "ru": "Замена экрана смартфона",  "en": "Phone screen replace",   "price": "60 ₼+"},
    "virus":      {"az": "Virus təmizliyi",            "ru": "Удаление вирусов",         "en": "Virus removal",          "price": "20 ₼"},
    "data":       {"az": "Məlumat bərpası",            "ru": "Восстановление данных",    "en": "Data recovery",          "price": "40 ₼+"},
    "ram":        {"az": "RAM / SSD yüksəltmə",        "ru": "Апгрейд RAM / SSD",        "en": "RAM / SSD upgrade",      "price": "20 ₼ (hissə ayrıca)"},
    "remote":     {"az": "Uzaqdan diaqnostika",        "ru": "Удалённая диагностика",    "en": "Remote diagnostics",     "price": "15 ₼"},
}

# ════════════════════════════════════════════
#  MƏTNLƏr / ТЕКСТЫ / TEXTS
# ════════════════════════════════════════════
TEXTS = {
    "welcome": {
        "az": (
            "🤖 <b>MR. ROBOT</b> — Texniki Xidmət Botuna xoş gəldiniz!\n\n"
            "Bu bot sizə probleminizi müəyyən etməyə və uyğun xidməti seçməyə kömək edəcək.\n\n"
            "Dil seçin 👇"
        ),
        "ru": (
            "🤖 <b>MR. ROBOT</b> — Добро пожаловать в бот технической поддержки!\n\n"
            "Этот бот поможет определить вашу проблему и выбрать нужную услугу.\n\n"
            "Выберите язык 👇"
        ),
        "en": (
            "🤖 <b>MR. ROBOT</b> — Welcome to the Tech Support Bot!\n\n"
            "This bot will help you identify your problem and choose the right service.\n\n"
            "Choose language 👇"
        ),
    },
    "choose_device": {
        "az": "📱 Hansı cihazda problem var?",
        "ru": "📱 С каким устройством проблема?",
        "en": "📱 What device has the problem?",
    },
    "choose_problem": {
        "az": "🔧 Problem nədir?",
        "ru": "🔧 В чём проблема?",
        "en": "🔧 What's the problem?",
    },
    "choose_service": {
        "az": "🛠️ Hansı xidməti seçirsiniz?",
        "ru": "🛠️ Какую услугу выбираете?",
        "en": "🛠️ Which service do you choose?",
    },
    "visit_type": {
        "az": "📍 Necə işləmək istərdiniz?",
        "ru": "📍 Как хотите работать?",
        "en": "📍 How would you like to proceed?",
    },
    "confirm": {
        "az": (
            "✅ <b>Sifariş qəbul edildi!</b>\n\n"
            "🤖 Ustamız tezliklə sizinlə əlaqə saxlayacaq.\n"
            "📲 Birbaşa əlaqə: <b>{contact}</b>\n\n"
            "<i>Adətən 15-30 dəqiqə ərzində cavab veririk.</i>"
        ),
        "ru": (
            "✅ <b>Заявка принята!</b>\n\n"
            "🤖 Наш мастер свяжется с вами в ближайшее время.\n"
            "📲 Прямой контакт: <b>{contact}</b>\n\n"
            "<i>Обычно отвечаем в течение 15-30 минут.</i>"
        ),
        "en": (
            "✅ <b>Request received!</b>\n\n"
            "🤖 Our technician will contact you shortly.\n"
            "📲 Direct contact: <b>{contact}</b>\n\n"
            "<i>We usually reply within 15-30 minutes.</i>"
        ),
    },
    "price_list": {
        "az": "💰 <b>Tam Qiymət Siyahısı</b>\n\n",
        "ru": "💰 <b>Полный прайс-лист</b>\n\n",
        "en": "💰 <b>Full Price List</b>\n\n",
    },
}

# Konversasiya mərhələləri
LANG, DEVICE, PROBLEM, SERVICE, VISIT = range(5)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ════════════════════════════════════════════
#  YARDIMÇI FUNKSİYALAR
# ════════════════════════════════════════════

def lang_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇦🇿 Azərbaycanca", callback_data="lang_az"),
        InlineKeyboardButton("🇷🇺 Русский",       callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English",       callback_data="lang_en"),
    ]])

def device_keyboard(lang):
    devices = {
        "az": [("💻 Noutbuk", "dev_nb"), ("🖥️ PC / Masa üstü", "dev_pc"), ("📱 Smartfon", "dev_ph"), ("⌨️ Planşet", "dev_tab")],
        "ru": [("💻 Ноутбук", "dev_nb"), ("🖥️ ПК / Десктоп",  "dev_pc"), ("📱 Смартфон", "dev_ph"), ("⌨️ Планшет",  "dev_tab")],
        "en": [("💻 Laptop",  "dev_nb"), ("🖥️ Desktop PC",    "dev_pc"), ("📱 Smartphone","dev_ph"), ("⌨️ Tablet",   "dev_tab")],
    }
    rows = []
    for label, data in devices[lang]:
        rows.append([InlineKeyboardButton(label, callback_data=data)])
    return InlineKeyboardMarkup(rows)

def problem_keyboard(lang, device):
    # Ümumi problemlər
    problems = {
        "az": [
            ("🐌 Yavaş işləyir",        "prob_slow"),
            ("🔥 Qızır / söndürülür",   "prob_heat"),
            ("💥 Ekran xarabdır",        "prob_screen"),
            ("🔇 Səs yoxdur",           "prob_sound"),
            ("🦠 Virus / zərərli proqram","prob_virus"),
            ("💾 Windows problemi",      "prob_win"),
            ("💧 Su düşüb",             "prob_water"),
            ("🔋 Batareya problemi",     "prob_bat"),
            ("❓ Digər problem",         "prob_other"),
        ],
        "ru": [
            ("🐌 Работает медленно",     "prob_slow"),
            ("🔥 Перегревается / выключается","prob_heat"),
            ("💥 Сломан экран",          "prob_screen"),
            ("🔇 Нет звука",            "prob_sound"),
            ("🦠 Вирус / вредоносное ПО","prob_virus"),
            ("💾 Проблема с Windows",    "prob_win"),
            ("💧 Попала вода",           "prob_water"),
            ("🔋 Проблема с батареей",   "prob_bat"),
            ("❓ Другая проблема",       "prob_other"),
        ],
        "en": [
            ("🐌 Running slow",          "prob_slow"),
            ("🔥 Overheating / shutting off","prob_heat"),
            ("💥 Screen broken",         "prob_screen"),
            ("🔇 No sound",             "prob_sound"),
            ("🦠 Virus / malware",       "prob_virus"),
            ("💾 Windows issue",         "prob_win"),
            ("💧 Water damage",          "prob_water"),
            ("🔋 Battery issue",         "prob_bat"),
            ("❓ Other problem",         "prob_other"),
        ],
    }
    rows = [[InlineKeyboardButton(l, callback_data=d)] for l, d in problems[lang]]
    return InlineKeyboardMarkup(rows)

def service_keyboard(lang, device, problem):
    # Problem → uyğun xidmətlər
    mapping = {
        "prob_slow":   ["clean", "ram", "windows", "virus"],
        "prob_heat":   ["clean", "diag_nb", "diag_pc"],
        "prob_screen": ["screen_nb", "screen_ph"],
        "prob_sound":  ["diag_nb", "diag_pc", "diag_pc"],
        "prob_virus":  ["virus", "windows"],
        "prob_win":    ["windows", "virus"],
        "prob_water":  ["diag_nb", "diag_pc"],
        "prob_bat":    ["diag_nb"],
        "prob_other":  ["diag_nb", "diag_pc", "remote"],
    }
    keys = mapping.get(problem, ["diag_nb", "diag_pc", "remote"])
    rows = []
    for key in keys:
        p = PRICES.get(key, {})
        label = f"{p.get(lang, key)} — {p.get('price','?')}"
        rows.append([InlineKeyboardButton(label, callback_data=f"svc_{key}")])
    return InlineKeyboardMarkup(rows)

def visit_keyboard(lang):
    opts = {
        "az": [
            ("🏠 Evinizə / ofisinizə gəlirik", "visit_home"),
            ("🔧 Özüm gətirəcəyəm",            "visit_bring"),
            ("🌐 Uzaqdan (remote)",              "visit_remote"),
        ],
        "ru": [
            ("🏠 Выезд к вам домой/в офис",    "visit_home"),
            ("🔧 Привезу сам",                  "visit_bring"),
            ("🌐 Удалённо (remote)",             "visit_remote"),
        ],
        "en": [
            ("🏠 Come to my home / office",     "visit_home"),
            ("🔧 I'll bring it myself",         "visit_bring"),
            ("🌐 Remote support",               "visit_remote"),
        ],
    }
    return InlineKeyboardMarkup([[InlineKeyboardButton(l, callback_data=d)] for l, d in opts[lang]])

# ════════════════════════════════════════════
#  HANDLERLƏr
# ════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    # Show welcome in all 3 langs simultaneously
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
    lang = query.data.split("_")[1]  # az / ru / en
    ctx.user_data["lang"] = lang
    await query.edit_message_text(
        TEXTS["choose_device"][lang],
        reply_markup=device_keyboard(lang),
        parse_mode="HTML"
    )
    return DEVICE

async def set_device(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = ctx.user_data["lang"]
    ctx.user_data["device"] = query.data
    await query.edit_message_text(
        TEXTS["choose_problem"][lang],
        reply_markup=problem_keyboard(lang, query.data),
        parse_mode="HTML"
    )
    return PROBLEM

async def set_problem(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = ctx.user_data["lang"]
    device = ctx.user_data["device"]
    problem = query.data
    ctx.user_data["problem"] = problem
    await query.edit_message_text(
        TEXTS["choose_service"][lang],
        reply_markup=service_keyboard(lang, device, problem),
        parse_mode="HTML"
    )
    return SERVICE

async def set_service(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = ctx.user_data["lang"]
    service_key = query.data.replace("svc_", "")
    ctx.user_data["service"] = service_key
    price_info = PRICES.get(service_key, {})
    ctx.user_data["service_name"] = price_info.get(lang, service_key)
    ctx.user_data["service_price"] = price_info.get("price", "?")
    await query.edit_message_text(
        TEXTS["visit_type"][lang],
        reply_markup=visit_keyboard(lang),
        parse_mode="HTML"
    )
    return VISIT

async def set_visit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = ctx.user_data["lang"]
    visit = query.data

    visit_labels = {
        "az": {"visit_home": "🏠 Evinizə gəlirik", "visit_bring": "🔧 Özüm gətirəcəyəm", "visit_remote": "🌐 Uzaqdan"},
        "ru": {"visit_home": "🏠 Выезд к вам",     "visit_bring": "🔧 Привезу сам",       "visit_remote": "🌐 Удалённо"},
        "en": {"visit_home": "🏠 Come to me",       "visit_bring": "🔧 I'll bring it",     "visit_remote": "🌐 Remote"},
    }

    user = query.from_user
    summary = (
        f"━━━━━━━━━━━━━━━\n"
        f"🤖 <b>YENİ SİFARİŞ / НОВАЯ ЗАЯВКА / NEW ORDER</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 {user.full_name} (@{user.username or 'yoxdur'})\n"
        f"🌐 Dil: {lang.upper()}\n"
        f"📱 Cihaz: {ctx.user_data.get('device','?')}\n"
        f"🔧 Problem: {ctx.user_data.get('problem','?')}\n"
        f"🛠️ Xidmət: {ctx.user_data.get('service_name','?')}\n"
        f"💰 Qiymət: {ctx.user_data.get('service_price','?')}\n"
        f"📍 Üsul: {visit_labels[lang].get(visit,'?')}\n"
        f"━━━━━━━━━━━━━━━"
    )

    # Admin-ə bildiriş göndər
    try:
        await ctx.bot.send_message(ADMIN_CHAT_ID, summary, parse_mode="HTML")
    except Exception as e:
        logger.warning(f"Admin notification failed: {e}")

    # İstifadəçiyə təsdiq
    confirm_text = TEXTS["confirm"][lang].format(contact=CONTACT)
    await query.edit_message_text(confirm_text, parse_mode="HTML")
    return ConversationHandler.END

async def price_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = ctx.user_data.get("lang", "az")
    text = TEXTS["price_list"][lang]
    for key, p in PRICES.items():
        name = p.get(lang, key)
        price = p.get("price", "?")
        text += f"• <b>{name}</b> — {price}\n"
    text += f"\n📲 {CONTACT}"
    await update.message.reply_html(text)

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Ləğv edildi / Отменено / Cancelled")
    return ConversationHandler.END

# ════════════════════════════════════════════
#  ƏSAS
# ════════════════════════════════════════════

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
    app.add_handler(CommandHandler("start", start))

    print("🤖 MR. ROBOT Bot işə düşdü / запущен / started...")
    app.run_polling()

if __name__ == "__main__":
    main()
