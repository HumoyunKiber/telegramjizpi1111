from telebot import types, TeleBot
import json
import os

main_bot = TeleBot('7347955276:AAHJNAodeVRJLxLlKvmJ_BMqinqlSCqcZSA')

def load_events():
    try:
        with open('events.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    events_button = types.KeyboardButton(text="📋 O'tkazilgan tadbirlar")
    search_button = types.KeyboardButton(text="🔍 Qidiruv")
    keyboard.add(events_button, search_button)
    return keyboard

def events_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    events = load_events()
    for index, event in enumerate(events, start=1):
        button = types.InlineKeyboardButton(text=f"{index}. {event['title']}", callback_data=f"event_{index}")
        keyboard.add(button)
    return keyboard

@main_bot.message_handler(commands=['start'])
def start_fun(message):
    main_bot.send_message(message.chat.id, "Tanlang:", reply_markup=main_keyboard())

@main_bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text
    if text == "📋 O'tkazilgan tadbirlar":
        main_bot.send_message(chat_id, "O'tkazilgan tadbirlar ro'yxati:", reply_markup=events_keyboard())
    elif text == "🔍 Qidiruv":
        main_bot.send_message(chat_id, "Qidiruvni boshlash uchun tadbir nomini yoki sanasini kiriting:")
        main_bot.register_next_step_handler(message, search_events)

def search_events(message):
    chat_id = message.chat.id
    query = message.text.lower()
    events = load_events()
    results = [event for event in events if query in event['title'].lower() or query in event['date']]

    if results:
        result_message = "Qidiruv natijalari:\n\n"
        for event in results:
            result_message += f"Tadbir: {event['title']}\nSana: {event['date']}\nBatafsil: {event['details']}\n\n"
        main_bot.send_message(chat_id, result_message)
    else:
        main_bot.send_message(chat_id, "Hech qanday tadbir topilmadi.")

@main_bot.callback_query_handler(func=lambda call: call.data.startswith("event_"))
def handle_event_callback(call):
    event_id = int(call.data.split("_")[1]) - 1
    events = load_events()

    if event_id < len(events):
        event = events[event_id]
        event_message = f"Tadbir: {event['title']}\n\nSana: {event['date']}\n\nBatafsil: {event['details']}\n\n"
        main_bot.send_message(call.message.chat.id, event_message)
        # Tadbir rasmlarini yuborish
        if event.get('photos'):
            for photo_path in event['photos']:
                try:
                    with open(photo_path, 'rb') as photo:
                        main_bot.send_photo(call.message.chat.id, photo)
                except Exception as e:
                    print("Rasmni yuborishda xatolik yuz berdi:", e)
        # Tadbir videolarini yuborish
        if event.get('videos'):
            for video_path in event['videos']:
                try:
                    with open(video_path, 'rb') as video:
                        main_bot.send_video(call.message.chat.id, video)
                except Exception as e:
                    print("Videoni yuborishda xatolik yuz berdi:", e)

if __name__ == '__main__':
    main_bot.infinity_polling()
