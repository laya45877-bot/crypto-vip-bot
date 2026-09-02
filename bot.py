import os
import logging
import sqlite3
from datetime import datetime, timedelta
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Logging စတင်ခြင်း
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

WEB_APP_URL = "https://crypto-vip-bot.vercel.app"

# Flask App စတင်ခြင်း (Mini App နဲ့ ချိတ်ဆက်ရန်)
app = Flask(__name__)
CORS(app)  # Vercel ဘက်ကနေ လှမ်းခေါ်တဲ့အခါ CORS Error မတက်အောင် ကာကွယ်ပေးသည်

def init_db():
    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            entry_ads_completed INTEGER DEFAULT 0,
            session_expiry TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 1. User ရဲ့ ကြော်ငြာနှင့် အချိန်အခြေအနေကို စစ်ဆေးမယ့် API
@app.route('/api/status/<int:user_id>', methods=['GET'])
def get_status(user_id):
    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT entry_ads_completed, session_expiry FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"entry_ads_completed": 0, "session_active": False})
    
    entry_done = row[0]
    expiry_str = row[1]
    
    session_active = False
    if expiry_str:
        expiry_time = datetime.fromisoformat(expiry_str)
        if datetime.now() < expiry_time:
            session_active = True
            
    return jsonify({
        "entry_ads_completed": entry_done,
        "session_active": session_active,
        "expiry_time": expiry_str
    })

# 2. စစချင်း ဝင်တဲ့အခါ ကြော်ငြာ ၂ ပုဒ် ကြည့်ပြီးကြောင်း မှတ်မယ့် API
@app.route('/api/entry_done', methods=['POST'])
def entry_done():
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "No user_id provided"})
        
    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET entry_ads_completed = 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# 3. အထဲမှာ ကြော်ငြာ ၃ ပုဒ် ကြည့်ပြီးလို့ ၁၀ မိနစ်စာ အချိန်တိုးပေးမယ့် API
@app.route('/api/session_done', methods=['POST'])
def session_done():
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "No user_id provided"})
        
    # လက်ရှိအချိန်မှ ၁၀ မိနစ် ထပ်ပေါင်းမည်
    new_expiry = (datetime.now() + timedelta(minutes=10)).isoformat()
    
    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET session_expiry = ? WHERE user_id = ?', (new_expiry, user_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "expiry_time": new_expiry})

# Flask ကို Background Thread ဖြင့် ဖွင့်ခြင်း
def run_flask():
    app.run(host='0.0.0.0', port=5000)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name if user and user.first_name else "ကိုကို"
    
    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT entry_ads_completed, session_expiry FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.execute('INSERT INTO users (user_id, entry_ads_completed, session_expiry) VALUES (?, 0, ?)', 
                       (user_id, datetime.now().isoformat()))
        conn.commit()
    
    conn.close()
    
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
    init_db()
    
    # Flask API ဆာဗာကို စတင်ခြင်း
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("Telegram Bot နှင့် API ဆာဗာပါ အလုပ်လုပ်နေပါပြီ...")
    application.run_polling()
