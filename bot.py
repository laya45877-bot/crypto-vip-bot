import os
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Telegram Bot Token
TOKEN = "8882874394:AAGbNWxRf4kcw8TY2GVvqiRhf8WhDIVjU"

# ယာယီ Database (User တစ်ဦးလျှင် Key တစ်ခုသေချာစေရန်)
user_keys = {}

async def handle_binance_slip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    user_name = user.first_name

    # User က ဓာတ်ပုံ (Slip) ပို့လာခြင်း ရှိမရှိ စစ်ဆေးခြင်း
    if update.message.photo:
        
        # ယခင်က Key ထုတ်ပေးပြီးသား ရှိမရှိ စစ်ဆေးခြင်း (One User, One Key)
        if user_id in user_keys:
            existing_key = user_keys[user_id]
            await update.message.reply_text(
                f"⚠️ ကိုကို ({user_name}) ရေ၊ သင့်အတွက် ထုတ်ပေးထားပြီးသား VIP Key ရှိနှင့်ပြီးပါပြီ:\n\n"
                f"🔑 `{existing_key}`\n\n"
                f"ဒီ Key ကို APK ထဲမှာ ထည့်သွင်းအသုံးပြုနိုင်ပါတယ်။",
                parse_mode="Markdown"
            )
            return

        # VIP Key အသစ် အလိုအလျောက် ထုတ်ပေးခြင်း
        generated_key = f"VIP-PRO-2026-{user_id}"
        user_keys[user_id] = generated_key

        # အောင်မြင်ကြောင်းနှင့် Key ပို့ပေးခြင်း
        success_msg = (
            f"🎉 **ကျေးဇူးတင်ပါတယ် ကိုကို {user_name} ရေ!**\n\n"
            f"✅ Binance ငွေလွဲပြေစာ (Slip) ကို စနစ်မှ အောင်မြင်စွာ လက်ခံရရှိပါပြီ။\n"
            f"🤖 သင့်အတွက် VIP Key ကို အလိုအလျောက် ထုတ်ပေးလိုက်ပါပြီ -\n\n"
            f"🔑 **VIP Key:** `{generated_key}`\n\n"
            f"💡 *ဒီ Key ကို ကိုကို့ရဲ့ APK ထဲမှာ ထည့်သွင်းပြီး VIP အပြည့်အစုံကို စတင်အသုံးပြုနိုင်ပါပြီ!*"
        )
        
        await update.message.reply_text(success_msg, parse_mode="Markdown")
        
    else:
        await update.message.reply_text(
            "📌 ကျေးဇူးပြု၍ Binance ငွေလွဲထားသော **Screenshot (Slip)** ပုံကိုသာ ပို့ပေးပါကိုကို။ "
            "ပုံပို့လိုက်တာနဲ့ Bot က စစ်ဆေးပြီး VIP Key ကို ချက်ချင်း ပို့ပေးပါလိမ့်မယ်။"
        )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_binance_slip))
    
    print("🤖 Binance VIP Bot အလုပ်လုပ်နေပါပြီ...")
    app.run_polling()

if __name__ == '__main__':
    main()
