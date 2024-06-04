from telebot import types
import telebot

# Replace with your actual bot token
bot = telebot.TeleBot('7205980664:AAGDHjBz4BQMM1OI7_j_V2f9EUxqIDj_RJA')

# Dictionary to store user language preferences
user_language = {}

def mainKeyboard(lang='uz'):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    if lang == 'uz':
        webAppTest = types.WebAppInfo("https://forms.gle/yn2m5NL95YtW77AE9")
        register_button = types.KeyboardButton(text="📝 Ro'yxatdan o'tish ✅", web_app=webAppTest)
    else:
        webAppTest = types.WebAppInfo("https://forms.gle/KYgVKdWEYR9TKd4u6")
        register_button = types.KeyboardButton(text="📝 Register ✅", web_app=webAppTest)
    
    chat_button = types.KeyboardButton(text="💬 Chat Bot")
    contact_operator_button = types.KeyboardButton(text="📞 Operator bilan bog'lanish" if lang == 'uz' else "📞 Contact Operator")
    
    address_webApp = types.WebAppInfo("https://maps.app.goo.gl/j6pvSVC6u6AsFmwK9")
    address_button = types.KeyboardButton(text="📍 Bizning manzil" if lang == 'uz' else "📍 Our Address", web_app=address_webApp)
    
    change_language_button = types.KeyboardButton(text="🌐 Tilni o'zgartirish" if lang == 'uz' else "🌐 Change Language")

    keyboard.add(register_button, chat_button)
    keyboard.add(contact_operator_button, address_button)
    keyboard.add(change_language_button)
    
    return keyboard

def inlineKeyboard(lang='uz'):
    keyboard = types.InlineKeyboardMarkup()
    chat_button = types.InlineKeyboardButton(text="💬 Chat Bot", url="https://t.me/jsuchatbot")
    keyboard.add(chat_button)
    return keyboard

@bot.message_handler(commands=['start'])
def start_fun(message):
    language_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    uz_button = types.KeyboardButton("🇺🇿 O'zbek tili")
    en_button = types.KeyboardButton("🇬🇧 English")
    language_keyboard.add(uz_button, en_button)
    
    bot.send_message(message.chat.id, "Tilni tanlang / Choose language:", reply_markup=language_keyboard)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text
    
    if text in ["🇺🇿 O'zbek tili", "🇬🇧 English"]:
        if text == "🇺🇿 O'zbek tili":
            user_language[chat_id] = 'uz'
            bot.send_message(chat_id, "Assalomu alaykum! Botimizga xush kelibsiz🤖.", reply_markup=mainKeyboard('uz'))
        else:
            user_language[chat_id] = 'en'
            bot.send_message(chat_id, "Hello! Welcome to our bot🤖.", reply_markup=mainKeyboard('en'))
        
        video = open('video_2024-05-31_16-37-43.mp4', 'rb')
        caption = "Universitet haqida video ma'lumot 🎥" if user_language[chat_id] == 'uz' else "Video information about the university 🎥"
        bot.send_video(chat_id, video, caption=caption)
    
    elif text == "💬 Chat Bot":
        bot.send_message(chat_id, "Chat botga o'tish uchun quyidagi tugmani bosing:" if user_language.get(chat_id) == 'uz' else "Click the button below to go to the chat bot:", reply_markup=inlineKeyboard(user_language.get(chat_id, 'uz')))
    
    elif text == "📞 Operator bilan bog'lanish":
        bot.send_message(chat_id, "Operator bilan bog'lanish uchun: +998 99 557 77 49" if user_language.get(chat_id) == 'uz' else "Contact operator at: +998 99 557 77 49")
    
    elif text == "🌐 Tilni o'zgartirish" or text == "🌐 Change Language":
        start_fun(message)

    else:
        start_fun(message)

@bot.message_handler(content_types=["video"])
def handle_video(message):
    bot.send_message(message.chat.id, "Rahmat!" if user_language.get(message.chat.id) == 'uz' else "Thank you!")

if __name__ == '__main__':
    bot.infinity_polling()
