import os
import logging
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Logging စတင်ခြင်း
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

WEB_APP_URL = "https://crypto-vip-bot.vercel.app"

# Database တည်ဆောက်ခြင်း (သို့မဟုတ် ချိတ်ဆက်ခြင်း)
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    # User တစ်ဦးချင်းစီရဲ့ Telegram ID, ဝင်ခွင့်အခြေအနေနဲ့ အချိန်ကို မှတ်မယ့်ဇယား
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            entry_ads_completed INTEGER DEFAULT 0,
            session_expiry TEXT
        )
    ''')
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name if user and user.first_name else "ကိုကို"
    
    # Database ထဲမှာ User ရှိမရှိ စစ်ဆေးပြီး မရှိသေးရင် အသစ်ထည့်မည်
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT entry_ads_completed, session_expiry FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.execute('INSERT INTO users (user_id, entry_ads_completed, session_expiry) VALUES (?, 0, ?)', 
                       (user_id, datetime.now().isoformat()))
        conn.commit()
    
    conn.close()
    
    # Mini App ဖွင့်ရန် ခလုတ်
    keyboard = [
        [InlineKeyboardButton("🚀 Crypto AI Signal Pro ဖွင့်ရန်", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        f"မင်္ဂလာပါ ကိုကို {user_name} 👋\n\n"
        "Crypto AI Signal Pro မှ ကြိုဆိုပါတယ်။ အောက်ပါခလုတ်ကိုနှိပ်ပြီး "
        "Mini App ကို ဝင်ရောက်အသုံးပြုနိုင်ပါပြီခင်ဗြာ။"
    )
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

if __name__ == '__main__':
    # Database ကို စတင်ဖန်တီးမည်
    init_db()
    
    BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("Telegram Bot နဲ့ Database အဆင်သင့် ဖြစ်ပါပြီ...")
    application.run_polling()
