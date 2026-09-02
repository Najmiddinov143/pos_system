import os
import sys
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram.request import HTTPXRequest
from telegram.error import BadRequest, TelegramError
from server.app.database import db

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

logging.basicConfig(level=logging.INFO)


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
        "📝 Qidirmoqchi bo'lgan mahsulot nomini yozib yuboring.",
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
    
    products = db.execute_query(
        "SELECT * FROM products WHERE name LIKE %s AND is_active = %s ORDER BY name LIMIT 50",
        (f"%{search_text}%", 1)
    )
    
    if not products:
        await update.message.reply_text(
            f"❌ *\"{search_text}\"* bo'yicha hech narsa topilmadi.",
            reply_markup=get_search_again_menu(),
            parse_mode='Markdown'
        )
        return
    
    text = f"🔍 *QIDIRUV NATIJASI:* \"{search_text}\"\n" + "═" * 30 + "\n\n"
    for p in products:
        status = "⚠️" if p[6] <= p[7] else "✅"
        text += f"{status} *{p[1]}*\n"
        text += f"   📊 Qoldiq: {p[6]} {p[8]}\n"
        text += f"   💰 Narx: {p[4]:,.0f} so'm\n\n"
    
    text += "═" * 30 + f"\n📋 Topildi: {len(products)} ta"
    await update.message.reply_text(text, reply_markup=get_search_again_menu(), parse_mode='Markdown')


# ============================================================
# 📦 OMBOR HOLATI
# ============================================================

async def show_inventory(query):
    products = db.execute_query("SELECT * FROM products WHERE is_active = %s ORDER BY name", (1,))
    
    if not products:
        await query.edit_message_text("📦 Ombor bo'sh!", reply_markup=get_back_menu())
        return
    
    text = "📦 *OMBOR HOLATI*\n" + "═" * 30 + "\n\n"
    low_stock = 0
    
    for p in products:
        status = "⚠️" if p[6] <= p[7] else "✅"
        if p[6] <= p[7]:
            low_stock += 1
        text += f"{status} *{p[1]}*\n"
        text += f"   📊 {p[6]} {p[8]}"
        if p[6] <= p[7]:
            text += f" (min: {p[7]})"
        text += f"\n   💰 {p[4]:,.0f} so'm\n\n"
    
    text += "═" * 30 + f"\n📊 Jami: {len(products)} ta\n⚠️ Kam qolgan: {low_stock} ta"
    await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')


# ============================================================
# 📊 BUGUNGI SAVDO
# ============================================================

async def show_today_sales(query):
    today = datetime.now().strftime('%Y-%m-%d')
    
    result = db.execute_one(
        "SELECT COALESCE(SUM(total_amount), 0), COALESCE(COUNT(*), 0), COALESCE(SUM(total_profit), 0) FROM sales WHERE DATE(created_at) = %s",
        (today,)
    )
    
    text = f"📊 *BUGUNGI SAVDO*\n" + "═" * 30 + f"\n📅 Sana: {today}\n💰 *Jami:* {result[0]:,.0f} so'm\n📋 Sotuvlar: {result[1]} ta\n💹 Foyda: {result[2]:,.0f} so'm"
    await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')


# ============================================================
# ⚠️ KAM QOLGAN MAHSULOTLAR
# ============================================================

async def show_low_stock(query):
    products = db.execute_query(
        "SELECT * FROM products WHERE quantity <= min_quantity AND is_active = %s ORDER BY quantity ASC",
        (1,)
    )
    
    if not products:
        await query.edit_message_text("✅ Barcha mahsulotlar yetarli miqdorda!", reply_markup=get_back_menu())
        return
    
    text = "⚠️ *KAM QOLGAN MAHSULOTLAR*\n" + "═" * 30 + "\n\n"
    for p in products:
        text += f"🔴 *{p[1]}*\n   📊 Qoldiq: {p[6]} {p[8]}\n   📉 Minimal: {p[7]}\n\n"
    
    text += "═" * 30 + f"\n📋 Jami: {len(products)} ta mahsulot kam qolgan"
    await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')


# ============================================================
# 🚗 NAVBAT
# ============================================================

async def show_queue(query):
    today = datetime.now().date()
    end_date = today + timedelta(days=3)
    
    queue = db.execute_query(
        """SELECT * FROM sales 
           WHERE DATE(next_oil_change_date) BETWEEN %s AND %s
           AND is_notified = %s
           ORDER BY next_oil_change_date ASC LIMIT 20""",
        (today, end_date, 0)
    )
    
    if not queue:
        await query.edit_message_text("✅ *Navbatda mijozlar yo'q!*", reply_markup=get_back_menu(), parse_mode='Markdown')
        return
    
    text = "🚗 *NAVBATDAGI MIJOZLAR*\n" + "═" * 30 + "\n\n"
    for i, q in enumerate(queue, 1):
        car_number = q[8] if q[8] else "Noma'lum"
        text += f"*{i}. 🚗 {car_number}*\n"
        text += f"   📅 Keyingi moy: {q[12]}\n"
        text += f"   💰 Summa: {q[1]:,.0f} so'm\n\n"
    
    text += "═" * 30 + f"\n📋 Jami: {len(queue)} ta mijoz navbatda"
    await query.edit_message_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')


# ============================================================
# 🔐 ADMIN PANEL
# ============================================================

async def admin_panel(query):
    await query.edit_message_text(
        "🔐 *Admin panel*\n\n"
        "📌 Parol: `/password admin123`\n"
        "• `/stats` - Umumiy statistika\n"
        "• `/sales` - Oxirgi sotuvlar",
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
    stats = db.execute_one(
        """SELECT 
            (SELECT COUNT(*) FROM products WHERE is_active = 1) as products,
            (SELECT COALESCE(SUM(cost_price * quantity), 0) FROM products WHERE is_active = 1) as total_cost,
            (SELECT COALESCE(SUM(sell_price * quantity), 0) FROM products WHERE is_active = 1) as total_value,
            (SELECT COALESCE(SUM(total_profit), 0) FROM sales) as total_profit,
            (SELECT COALESCE(COUNT(*), 0) FROM sales) as total_sales"""
    )
    
    text = "🔐 *ADMIN PANEL*\n" + "═" * 30 + "\n\n"
    text += f"📦 Mahsulotlar: {stats[0]}\n💰 Tannarx: {stats[1]:,.0f} so'm\n💵 Qiymat: {stats[2]:,.0f} so'm\n🏆 Jami foyda: {stats[3]:,.0f} so'm\n📋 Jami sotuv: {stats[4]} ta"
    
    await update.message.reply_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_admin_stats(update)


async def sales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sales = db.execute_query("SELECT * FROM sales ORDER BY created_at DESC LIMIT 20")
    
    if not sales:
        await update.message.reply_text("📋 Sotuvlar yo'q!")
        return
    
    text = "📋 *OXIRGI SOTUVLAR*\n" + "═" * 30 + "\n\n"
    for s in sales:
        text += f"#{s[0]} 🕐 {s[4][:16]}\n💰 {s[1]:,.0f} so'm\n\n"
    
    await update.message.reply_text(text, reply_markup=get_back_menu(), parse_mode='Markdown')


# ============================================================
# BOTNI ISHGA TUSHIRISH
# ============================================================

def run_bot():
    try:
        request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
        app = Application.builder().token(TOKEN).request(request).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("password", password_handler))
        app.add_handler(CommandHandler("stats", stats_command))
        app.add_handler(CommandHandler("sales", sales_command))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        
        print("🤖 Telegram bot ishga tushdi!")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"❌ Bot xatosi: {e}")


if __name__ == "__main__":
    run_bot()