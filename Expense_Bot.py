import telebot
from pymongo import MongoClient
import datetime
from flask import Flask
from threading import Thread
import os

# 1. Apna Token aur MongoDB URL yahan dalein
TOKEN = '8855710390:AAF2a9LYiOpmDLuO0rOD10g3n__A4WE8Vh0'
MONGO_URI = 'mongodb://localhost:27017'
bot = telebot.TeleBot(TOKEN)

# --- Dummy Web Server (Render 24/7 ke liye zaroori hai) ---
app = Flask(name)

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

server_thread = Thread(target=run_server)
server_thread.start()
# -----------------------------------------------------------

try:
    client = MongoClient(MONGO_URI)
    db = client['telegram_bot_db'] 
    expenses_collection = db['expenses'] 
except Exception as e:
    print(f"MongoDB connection me error: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "Welcome! Main aapka 24/7 Cloud Expense Tracker Bot hoon. ☁️💰\n\nAdd: /add 150 Khana\nTotal: /total"
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['add'])
def add_expense(message):
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, "❌ Sahi format: /add 150 Khana", parse_mode="Markdown")
            return
        
        amount = float(parts[1])
        category = parts[2]
        
        expense_data = {
            "user_id": message.chat.id,
            "amount": amount,
            "category": category,
            "date": datetime.date.today().strftime("%Y-%m-%d")
        }

        expenses_collection.insert_one(expense_data)
        bot.reply_to(message, f"✅ Done! ₹{amount} '{category}' ke liye save ho gaya.")
    except ValueError:
        bot.reply_to(message, "⚠️ Amount ki jagah sirf number likhein!")

@bot.message_handler(commands=['total'])
def show_total(message):
    user_expenses = list(expenses_collection.find({"user_id": message.chat.id}))
    if len(user_expenses) == 0:
        bot.reply_to(message, "🤷‍♂️ Aapne abhi tak koi kharcha add nahi kiya hai.")
        return
    
    total = sum(exp['amount'] for exp in user_expenses)
    details = "📝 Aapke Kharch ki List:\n\n"
    for exp in user_expenses:
        details += f"🔸 {exp['category']}: ₹{exp['amount']} *(on {exp['date']})*\n"
    
    details += f"\n💰 Total Kharcha: ₹{total}"
    bot.reply_to(message, details, parse_mode="Markdown")

bot.polling(none_stop=True)