# telegram_bot.py
import os
import sys
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# ===== YO'LNI ANIQLASH =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram.request import HTTPXRequest
from telegram.error import BadRequest, TelegramError

# ===== KONFIGURATSIYA =====
TOKEN = "8520222825:8804348618:AAGChnE_w9jusklKSj9UmotvE8cnxH2BYjk"  # yoki os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = 1851119080  # Sizning Telegram IDingiz

logging.basicConfig(level=logging.INFO)

# ===== DATABASE =====
# Agar sizning db modulingiz bo'lsa:
# from server.app.database import db

# Yoki oddiy sqlite3 ishlatish uchun:
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "pos.db")

def get_db_connection():
    """Ma'lumotlar bazasiga ulanish"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=()):
    """SELECT so'rovlarini bajarish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

def execute_one(query, params=()):
    """Bitta natija qaytaradigan SELECT so'rovi"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    return result


# ===== MENU TUGMALARI =====
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🔍 Qidirish", callback_data="search")],
        [InlineKeyboardButton("📦 Ombor holati", callback_data="inventory")],
        [InlineKeyboardButton("📊 Bugungi savdo", callback_data="today")],
        [InlineKeyboardButton("⚠️ Kam qolgan mahsulotlar", callback_data="low_stock")],
        [InlineKeyboardButton("🚗 Navbat", callback_data="queue")],
        [InlineKeyboardButton("🔐 Admin panel", callback_data="admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_menu():
    keyboard = [[InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)

def get_search_again_menu():
    keyboard = [
        [InlineKeyboardButton("🔍 Yana qidirish", callback_data="search")],
        [InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================================
# BOT HANDLERLAR
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Admin tekshiruvi (ixtiyoriy)
    if user_id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ Sizga ruxsat yo'q!")
        return
    
    context.user_data['awaiting_search'] = False
    welcome_text = (
        "🏪 *POS Tizimi Botiga xush kelibsiz!*\n\n"
        "📌 *Moy almashtirish ustalari uchun bot*\n"
        "⚡ Quyidagi tugmalardan birini tanlang:"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu(), parse_mode='Markdown')


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    try:
        await query.answer()
    except Exception:
        pass

    try:
        if query.data == "main_menu":
            context.user_data["awaiting_search"] = False
            await show_main_menu(query)
        elif query.data == "search":
            await show_search_prompt(query, context)
        elif query.data == "inventory":
            await show_inventory(query)
        elif query.data == "today":
            await show_today_sales(query)
        elif query.data == "low_stock":
            await show_low_stock(query)
        elif query.data == "queue":
            await show_queue(query)
        elif query.data == "admin":
            await admin_panel(query)
    except Exception as e:
        print(f"❌ Xatolik: {e}")


async def show_main_menu(query):
    welcome_text = (
        "🏪 *POS Tizimi Botiga xush kelibsiz!*\n\n"
        "📌 *Moy almashtirish ustalari uchun bot*\n"
        "⚡ Quyidagi tugmalardan birini tanlang:"
    )
    await query.edit_message_text(welcome_text, reply_markup=get_main_menu(), parse_mode='Markdown')


# ============================================================
# 🔍 QIDIRUV
# ============================================================

async def show_search_prompt(query, context):
    context.user_data['awaiting_search'] = True
    await query.edit_message_text(
        "🔍 *Mahsulot qidirish*\n\n"
        "📝 Qidirmoqchi bo'lgan mahsulot nomini yozib yuboring.\n"
        "Masalan: `Fosser` yoki `filter`",
        reply_markup=get_back_menu(),
        parse_mode='Markdown'
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_search'):
        return
    
    search_text = update.message.text.strip()
    context.user_data['awaiting_search'] = False
    
    if not search_text:
        await update.message.reply_text("❌ Iltimos, mahsulot nomini yozing.", reply_markup=get_search_again_menu())
        return
    
    # SQLite uchun %s o'rniga ? ishlatiladi
    products = execute_query(
        "SELECT * FROM products WHERE name LIKE ? AND is_active = 1 ORDER BY name LIMIT 50",
        (f"%{search_text}%",)
    )
    
    if not products:
        await update.message.reply_text(
            f"❌ *\"{search_text}\"* bo'yicha hech narsa topilmadi.",
            reply_markup=get_search_again_menu(),
            parse_mode='Markdown'
        )
        return
    
    text = f"🔍 *QIDIRUV NATIJASI:* \"{search_text}\"\n"
    text += "═" * 30 + "\n\n"
    
    for p in products:
        status = "⚠️" if p['quantity'] <= p['min_quantity'] else "✅"
        text += f"{status} *{p['name']}*\n"
        text += f"   📊 Qoldiq: {p['quantity']} {p['unit']}\n"
        text += f"   💰 Narx: {p['sell_price']:,.0f} so'm\n\n"
    
    text += "═" * 30 + f"\n📋 Topildi: {len(products)} ta"
    await update.message.reply_text(text, reply_markup=get_search_again_menu(), parse_mode='Markdown')


# ============================================================
# 📦 OMBOR HOLATI
# ============================================================

async def show_inventory(query):
    products = execute_query("SELECT * FROM products WHERE is_active = 1 ORDER BY name")
    
    if not products:
        await query.edit_message_text("📦 Ombor bo'sh!", reply_markup=get_back_menu())
        return
    
    text = "📦 *OMBOR HOLATI*\n"
    text += "═" * 30 + "\n\n"
    low_stock = 0
    
    for p in products:
        status = "⚠️" if p['quantity'] <= p['min_quantity'] else "✅"
        if p['quantity'] <= p['min_quantity']:
            low_stock += 1
        text += f"{status} *{p['name']}*\n"
        text += f"   📊 {p['quantity']} {p['unit']}"
        if p['quantity'] <= p['min_quantity']:
            text += f" (min: {p['min_quantity']})"
        text += f"\n   💰 {p['sell_price']:,.0f} so'm\n\n"
    
    text += "═" * 30 + f"\n📊 Jami: {len(products)} ta\n⚠️ Kam qolgan: {low_stock} ta"
    await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')


# ============================================================
# 📊 BUGUNGI SAVDO
# ============================================================

async def show_today_sales(query):
    today = datetime.now().strftime('%Y-%m-%d')
    
    result = execute_one(
        "SELECT COALESCE(SUM(total_amount), 0), COALESCE(COUNT(*), 0), COALESCE(SUM(total_profit), 0) FROM sales WHERE DATE(created_at) = ?",
        (today,)
    )
    
    # Agar result None bo'lsa
    if result:
        total, count, profit = result[0], result[1], result[2]
    else:
        total, count, profit = 0, 0, 0
    
    text = f"📊 *BUGUNGI SAVDO*\n"
    text += "═" * 30 + "\n"
    text += f"📅 Sana: {today}\n"
    text += f"💰 *Jami:* {total:,.0f} so'm\n"
    text += f"📋 Sotuvlar: {count} ta\n"
    text += f"💹 Foyda: {profit:,.0f} so'm"
    
    await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')


# ============================================================
# ⚠️ KAM QOLGAN MAHSULOTLAR
# ============================================================

async def show_low_stock(query):
    products = execute_query(
        "SELECT * FROM products WHERE quantity <= min_quantity AND is_active = 1 ORDER BY quantity ASC"
    )
    
    if not products:
        await query.edit_message_text("✅ Barcha mahsulotlar yetarli miqdorda!", reply_markup=get_back_menu())
        return
    
    text = "⚠️ *KAM QOLGAN MAHSULOTLAR*\n"
    text += "═" * 30 + "\n\n"
    
    for p in products:
        text += f"🔴 *{p['name']}*\n"
        text += f"   📊 Qoldiq: {p['quantity']} {p['unit']}\n"
        text += f"   📉 Minimal: {p['min_quantity']}\n\n"
    
    text += "═" * 30 + f"\n📋 Jami: {len(products)} ta mahsulot kam qolgan"
    await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')


# ============================================================
# 🚗 NAVBAT
# ============================================================

async def show_queue(query):
    today = datetime.now().date()
    end_date = today + timedelta(days=3)
    
    queue = execute_query(
        """SELECT s.*, u.username 
           FROM sales s
           LEFT JOIN users u ON s.user_id = u.id
           WHERE DATE(s.next_oil_change_date) BETWEEN ? AND ?
           AND s.is_notified = 0
           ORDER BY s.next_oil_change_date ASC LIMIT 20""",
        (today, end_date)
    )
    
    if not queue:
        await query.edit_message_text(
            "✅ *Navbatda mijozlar yo'q!*\n\n🚗 Hozircha keladigan mijozlar yo'q.",
            reply_markup=get_back_menu(),
            parse_mode='Markdown'
        )
        return
    
    text = "🚗 *NAVBATDAGI MIJOZLAR*\n"
    text += "═" * 30 + "\n\n"
    
    for i, q in enumerate(queue, 1):
        car_number = q['car_number'] if q['car_number'] else "Noma'lum"
        text += f"*{i}. 🚗 {car_number}*\n"
        if q['car_model']:
            text += f"   📌 Model: {q['car_model']}\n"
        text += f"   📅 Keyingi moy: {q['next_oil_change_date']}\n"
        text += f"   💰 Summa: {q['total_amount']:,.0f} so'm\n\n"
    
    text += "═" * 30 + f"\n📋 Jami: {len(queue)} ta mijoz navbatda"
    await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')


# ============================================================
# 🔐 ADMIN PANEL
# ============================================================

async def admin_panel(query):
    await query.edit_message_text(
        "🔐 *Admin panel*\n\n"
        "📌 Barcha ma'lumotlarni ko'rish uchun parolni kiriting:\n"
        "`/password admin123`\n\n"
        "📌 Yoki quyidagi buyruqlarni ishlating:\n"
        "• `/stats` - Umumiy statistika\n"
        "• `/sales` - Oxirgi sotuvlar\n"
        "• `/qidir <nomi>` - Mahsulot qidirish",
        reply_markup=get_back_menu(),
        parse_mode='Markdown'
    )


async def password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    password = text.replace('/password ', '').strip()
    
    if password == "admin123":
        await show_admin_stats(update)
    else:
        await update.message.reply_text("❌ Noto'g'ri parol!")


async def show_admin_stats(update):
    stats = execute_one(
        """SELECT 
            (SELECT COUNT(*) FROM products WHERE is_active = 1) as products,
            (SELECT COALESCE(SUM(cost_price * quantity), 0) FROM products WHERE is_active = 1) as total_cost,
            (SELECT COALESCE(SUM(sell_price * quantity), 0) FROM products WHERE is_active = 1) as total_value,
            (SELECT COALESCE(SUM(total_profit), 0) FROM sales) as total_profit,
            (SELECT COALESCE(COUNT(*), 0) FROM sales) as total_sales"""
    )
    
    text = "🔐 *ADMIN PANEL*\n"
    text += "═" * 30 + "\n\n"
    text += "📊 *UMUMIY STATISTIKA*\n"
    text += f"📦 Mahsulotlar: {stats[0]}\n"
    text += f"💰 Tannarx: {stats[1]:,.0f} so'm\n"
    text += f"💵 Qiymat: {stats[2]:,.0f} so'm\n"
    text += f"🏆 Jami foyda: {stats[3]:,.0f} so'm\n"
    text += f"📋 Jami sotuv: {stats[4]} ta"
    
    await update.message.reply_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_admin_stats(update)


async def sales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sales = execute_query("SELECT * FROM sales ORDER BY created_at DESC LIMIT 20")
    
    if not sales:
        await update.message.reply_text("📋 Sotuvlar yo'q!")
        return
    
    text = "📋 *OXIRGI SOTUVLAR*\n"
    text += "═" * 30 + "\n\n"
    
    for s in sales:
        text += f"#{s['id']} "
        text += f"🕐 {s['created_at'][:16]}\n"
        text += f"💰 {s['total_amount']:,.0f} so'm"
        if s['car_number']:
            text += f" | 🚗 {s['car_number']}"
        text += "\n\n"
    
    await update.message.reply_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')


# ============================================================
# XATOLIKLARNI USHLASH
# ============================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"⚠️ Bot xatosi: {context.error}")


# ============================================================
# BOTNI ISHGA TUSHIRISH
# ============================================================

def run_bot():
    """Botni ishga tushirish"""
    try:
        request = HTTPXRequest(
            connect_timeout=30.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=30.0,
        )
        
        app = Application.builder().token(TOKEN).request(request).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("password", password_handler))
        app.add_handler(CommandHandler("stats", stats_command))
        app.add_handler(CommandHandler("sales", sales_command))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        app.add_error_handler(error_handler)
        
        print("=" * 50)
        print("🤖 Telegram bot ishga tushdi!")
        print("📱 Botni oching va /start yozing")
        print("=" * 50)
        
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"❌ Bot xatosi: {e}")


# ============================================================
# ASOSIY
# ============================================================

if __name__ == "__main__":
    # database papkasini yaratish
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    run_bot()