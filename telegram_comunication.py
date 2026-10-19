import telebot
import subprocess

TOKEN = "הטוקן_שלך_כאן"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, "חושב...")
    try:
        # מריץ את קלוד במצב לא אינטראקטיבי
        result = subprocess.run(
            ["claude", "-p", "--no-session-persistence", message.text],
            capture_output=True, text=True, check=True
        )
        bot.send_message(message.chat.id, result.stdout if result.stdout else "בוצע (ללא פלט חזרה).")
    except subprocess.CalledProcessError as e:
        bot.send_message(message.chat.id, f"שגיאה מול קלוד:\n{e.stderr}")

bot.infinity_polling()