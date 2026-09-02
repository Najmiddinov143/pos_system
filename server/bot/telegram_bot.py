import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sys
sys.path.append('/app')
from server.app.database import db

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ Sizga ruxsat yo'q!")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Bugungi savdo", callback_data="today_sales")],
        [InlineKeyboardButton("📦 Mahsulotlar soni", callback_data="products_count")],
        [InlineKeyboardButton("⚠️ Kam qolganlar", callback_data="low_stock")],
        [InlineKeyboardButton("📋 So'nggi savdolar", callback_data="recent_sales")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 POS System Botga xush kelibsiz!", reply_markup=reply_markup)

async def today_sales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    result = db.execute_one("SELECT COALESCE(SUM(total_amount), 0) FROM sales WHERE DATE(created_at) = CURRENT_DATE")
    await query.edit_message_text(f"📊 Bugungi savdo: {result[0]:,.0f} so'm")

async def products_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    result = db.execute_one("SELECT COUNT(*) FROM products")
    await query.edit_message_text(f"📦 Jami mahsulotlar: {result[0]} ta")

async def low_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    result = db.execute_one("SELECT COUNT(*) FROM products WHERE quantity <= min_quantity")
    await query.edit_message_text(f"⚠️ Kam qolgan mahsulotlar: {result[0]} ta")

async def recent_sales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sales = db.execute_query("SELECT id, total_amount, created_at FROM sales ORDER BY id DESC LIMIT 5")
    if not sales:
        await query.edit_message_text("📋 Hozircha savdo yo'q")
        return
    text = "📋 So'nggi 5 ta savdo:\n\n"
    for s in sales:
        text += f"🆔 #{s[0]} | {s[1]:,.0f} so'm | {s[2]}\n"
    await query.edit_message_text(text)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(today_sales, pattern="today_sales"))
    app.add_handler(CallbackQueryHandler(products_count, pattern="products_count"))
    app.add_handler(CallbackQueryHandler(low_stock, pattern="low_stock"))
    app.add_handler(CallbackQueryHandler(recent_sales, pattern="recent_sales"))
    print("🤖 Telegram bot ishga tushdi!")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
