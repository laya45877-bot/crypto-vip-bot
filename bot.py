import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Logging ကို စတင်ခြင်း
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Mini App ရဲ့ Vercel Link (ကိုကို့ရဲ့ Link အမှန်နဲ့ ထည့်ပါ)
WEB_APP_URL = "https://crypto-vip-bot.vercel.app"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_name = user.first_name if user and user.first_name else "ကိုကို"
    
    # Mini App ကို ဖွင့်ရန် WebApp button ချိတ်ဆက်ခြင်း
    keyboard = [
        [InlineKeyboardButton("🚀 Crypto AI Signal Pro ဖွင့်ရန်", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        f"မင်္ဂလာပါ ကိုကို {user_name} 👋\n\n"
        "Crypto AI Signal Pro မှ ကြိုဆိုပါတယ်။ အောက်ပါခလုတ်ကိုနှိပ်ပြီး "
        "Mini App ကို ဝင်ရောက်ကာ အသုံးပြုနိုင်ပါပြီခင်ဗြာ။"
    )
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

if __name__ == '__main__':
    # Telegram Bot Token ထည့်ရန် (သို့မဟုတ် Environment Variable မှ ယူရန်)
    BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    print("Telegram Bot စတင် အလုပ်လုပ်နေပါပြီ...")
    application.run_polling()
