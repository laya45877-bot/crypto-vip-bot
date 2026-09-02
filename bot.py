from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Frontend ကနေ လှမ်းချိတ်လို့ရအောင် CORS ခွင့်ပြုပေးခြင်း

DB_NAME = "database.db"

# ဇယားဖန်တီးခြင်း (Database Initialization)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            has_key INTEGER DEFAULT 0,
            expiry_date TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ၁။ User ရဲ့ လက်ရှိအခြေအနေကို စစ်ဆေးခြင်း
@app.route('/api/check_status/<user_id>', methods=['GET'])
def check_status(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT has_key, expiry_date FROM users WHERE user_id = ?', (str(user_id),))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True, "has_key": bool(user[0]), "expiry_date": user[1]})
    else:
        return jsonify({"success": True, "has_key": False, "expiry_date": None})

# ၂။ ပထမအကြိမ်အတွက် ရက် ၃၀ Key အသစ် ထုတ်ပေးခြင်း (တစ်သက်မှာ တစ်ကြိမ်သာ)
@app.route('/api/generate_key', methods=['POST'])
def generate_key():
    data = request.json
    user_id = str(data.get('user_id'))

    if not user_id:
        return jsonify({"success": False, "message": "User ID is required"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # ဒီ User မှာ Key အရင်က ရှိပြီးသားလား ထပ်စစ်မယ်
    cursor.execute('SELECT has_key FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    now = datetime.now()
    expiry = now + timedelta(days=30)
    expiry_str = expiry.strftime('%Y-%m-%d %H:%M:%S')

    if user and user[0] == 1:
        # ပြီးသွားပြီသားဆိုရင် Key အသစ်ထပ်မထုတ်ပေးတော့ဘဲ ရှိပြီးသားကိုပဲ ပြန်သုံးခွင့်ပေးမယ်
        conn.close()
        return jsonify({"success": True, "message": "Key already exists (One-time only)"})

    # မရှိသေးရင် ရက် ၃၀ စာ Key အသစ် အတည်ပြုပေးမည်
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, has_key, expiry_date, created_at)
        VALUES (?, 1, ?, ?)
    ''', (user_id, expiry_str, now.strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Free 30-day key generated successfully", "expiry_date": expiry_str})

# ၃။ ရက် ၃၀ အတွင်း ပြန်လည်ဝင်ရောက်ခြင်း (Re-entry)
@app.route('/api/reentry', methods=['POST'])
def reentry():
    data = request.json
    user_id = str(data.get('user_id'))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT has_key FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user and user[0] == 1:
        return jsonify({"success": True, "message": "Re-entry allowed"})
    else:
        return jsonify({"success": False, "message": "No active key found"})

if __name__ == '__main__':
    app.run(debug=True)
