from telebot import types, TeleBot
import json
import os
from datetime import datetime

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}

admin_bot = TeleBot('6917757900:AAEPlWgJ1lvQ8SLqFzVLpY8b0DEeKiLkJM0')
user_data = {}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_events():
    try:
        with open('events.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_events(events):
    with open('events.json', 'w', encoding='utf-8') as file:
        json.dump(events, file, ensure_ascii=False, indent=4)

def main_keyboard(language):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if language == 'uz':
        events_button = types.KeyboardButton(text="📝 Tadbirlar ro'yxati")
        add_event_button = types.KeyboardButton(text="✅ Yangi tadbir qo'shish")
        change_language_button = types.KeyboardButton(text="🌐 Tilni o'zgartirish")
    elif language == 'en':
        events_button = types.KeyboardButton(text="📝 List of Events")
        add_event_button = types.KeyboardButton(text="✅ Add New Event")
        change_language_button = types.KeyboardButton(text="🌐 Change Language")
    keyboard.add(events_button, add_event_button)
    keyboard.add(change_language_button)
    return keyboard

def events_keyboard(events, language):
    keyboard = types.InlineKeyboardMarkup()
    for index, event in enumerate(events, start=1):
        button_view = types.InlineKeyboardButton(text=f"{index}. {event['title']}", callback_data=f"view_{index}")
        if language == 'uz':
            button_delete = types.InlineKeyboardButton(text="❌ O'chirish", callback_data=f"delete_{index}")
        elif language == 'en':
            button_delete = types.InlineKeyboardButton(text="❌ Delete", callback_data=f"delete_{index}")
        keyboard.add(button_view, button_delete)
    return keyboard

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    admin_bot.send_message(chat_id, "Please enter your login:")
    admin_bot.register_next_step_handler(message, get_login)

def get_login(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'login': message.text}
    admin_bot.send_message(chat_id, "Please enter your password:")
    admin_bot.register_next_step_handler(message, get_password)

def get_password(message):
    chat_id = message.chat.id
    password = message.text
    login = user_data[chat_id].get('login')

    if login == 'Humoyun' and password == 'Humoyun1312':
        language_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        uz_button = types.KeyboardButton(text="🇺🇿 O'zbek tili")
        en_button = types.KeyboardButton(text="🇺🇸 English")
        language_keyboard.add(uz_button, en_button)
        admin_bot.send_message(chat_id, "Tilni tanlang / Choose a language:", reply_markup=language_keyboard)
    else:
        admin_bot.send_message(chat_id, "Login or password incorrect. Please try again.")
        start_message(message)

@admin_bot.message_handler(func=lambda message: message.text in ["🇺🇿 O'zbek tili", "🇺🇸 English"])
def choose_language(message):
    chat_id = message.chat.id
    if message.text == "🇺🇿 O'zbek tili":
        language = 'uz'
        admin_bot.send_message(chat_id, "Til tanlandi: O'zbek tili", reply_markup=main_keyboard(language))
    elif message.text == "🇺🇸 English":
        language = 'en'
        admin_bot.send_message(chat_id, "Language selected: English", reply_markup=main_keyboard(language))
    
    user_data[chat_id]['language'] = language

@admin_bot.message_handler(func=lambda message: message.text in ["📝 Tadbirlar ro'yxati", "📝 List of Events"])
def show_events(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    events = load_events()
    if events:
        if language == 'uz':
            admin_bot.send_message(chat_id, "O'tkazilgan tadbirlar ro'yxati:", reply_markup=events_keyboard(events, language))
        elif language == 'en':
            admin_bot.send_message(chat_id, "List of held events:", reply_markup=events_keyboard(events, language))
    else:
        if language == 'uz':
            admin_bot.send_message(chat_id, "O'tkazilgan tadbirlar mavjud emas.")
        elif language == 'en':
            admin_bot.send_message(chat_id, "No events available.")

@admin_bot.message_handler(func=lambda message: message.text in ["✅ Yangi tadbir qo'shish", "✅ Add New Event"])
def add_event(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    if language == 'uz':
        admin_bot.send_message(chat_id, "Tadbir nomini kiriting:")
    elif language == 'en':
        admin_bot.send_message(chat_id, "Enter the event name:")
    admin_bot.register_next_step_handler(message, get_event_title)

@admin_bot.message_handler(func=lambda message: message.text in ["🌐 Tilni o'zgartirish", "🌐 Change Language"])
def change_language(message):
    start_message(message)

def get_event_title(message):
    chat_id = message.chat.id
    user_event = {'title': message.text, 'photos': [], 'videos': []}
    user_data[chat_id]['event'] = user_event
    language = user_data[chat_id]['language']
    if language == 'uz':
        admin_bot.send_message(chat_id, "Tadbir o'tkazilgan sanasini kiriting (yyyy-mm-dd):")
    elif language == 'en':
        admin_bot.send_message(chat_id, "Enter the event date (yyyy-mm-dd):")
    admin_bot.register_next_step_handler(message, get_event_date)

def get_event_date(message):
    chat_id = message.chat.id
    date_text = message.text
    language = user_data[chat_id]['language']
    if not validate_date(date_text):
        if language == 'uz':
            admin_bot.send_message(chat_id, "Sana noto'g'ri formatda kiritildi. Iltimos sana formatini to'g'ri yozing (yyyy-mm-dd):")
        elif language == 'en':
            admin_bot.send_message(chat_id, "The date is in an incorrect format. Please enter the date correctly (yyyy-mm-dd):")
        admin_bot.register_next_step_handler(message, get_event_date)
        return
    user_data[chat_id]['event']['date'] = date_text
    if language == 'uz':
        admin_bot.send_message(chat_id, "Tadbir haqida batafsil ma'lumot kiriting:")
    elif language == 'en':
        admin_bot.send_message(chat_id, "Enter detailed information about the event:")
    admin_bot.register_next_step_handler(message, get_event_details)

def get_event_details(message):
    chat_id = message.chat.id
    user_data[chat_id]['event']['details'] = message.text
    language = user_data[chat_id]['language']
    send_photo_prompt(chat_id, language)

def send_photo_prompt(chat_id, language):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if language == 'uz':
        finish_button = types.KeyboardButton(text="Tugatish")
        prompt_message = "Rasmni yuboring yoki 'Tugatish' tugmasini bosing:"
    elif language == 'en':
        finish_button = types.KeyboardButton(text="Finish")
        prompt_message = "Send the photo or press 'Finish' button:"
    keyboard.add(finish_button)
    admin_bot.send_message(chat_id, prompt_message, reply_markup=keyboard)
    admin_bot.register_next_step_handler_by_chat_id(chat_id, get_event_photos)

def send_video_prompt(chat_id, language):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if language == 'uz':
        finish_button = types.KeyboardButton(text="Tugatish")
        prompt_message = "Video yuboring yoki 'Tugatish' tugmasini bosing:"
    elif language == 'en':
        finish_button = types.KeyboardButton(text="Finish")
        prompt_message = "Send the video or press 'Finish' button:"
    keyboard.add(finish_button)
    admin_bot.send_message(chat_id, prompt_message, reply_markup=keyboard)
    admin_bot.register_next_step_handler_by_chat_id(chat_id, get_event_videos)

def save_file(file_id, file_type):
    file_info = admin_bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = admin_bot.download_file(file_path)

    file_extension = file_path.split('.')[-1]
    file_name = f"{file_id}.{file_extension}"
    file_full_path = os.path.join(UPLOAD_FOLDER, file_name)

    with open(file_full_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    return file_full_path

def get_event_photos(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    
    if message.text and (message.text.lower() == 'tugatish' or message.text.lower() == 'finish'):
        send_video_prompt(chat_id, language)
        return

    if message.content_type == 'photo':
        photo_id = message.photo[-1].file_id
        photo_path = save_file(photo_id, 'photo')
        user_data[chat_id]['event']['photos'].append(photo_path)
    else:
        if language == 'uz':
            admin_bot.send_message(chat_id, "Rasm yuborilmadi. Rasmni yuboring yoki 'Tugatish' tugmasini bosing:")
        elif language == 'en':
            admin_bot.send_message(chat_id, "No photo was sent. Send the photo or press 'Finish' button:")
        admin_bot.register_next_step_handler(message, get_event_photos)
        return

    if language == 'uz':
        admin_bot.send_message(chat_id, "Yana rasm yuborishingiz mumkin yoki 'Tugatish' tugmasini bosing:")
    elif language == 'en':
        admin_bot.send_message(chat_id, "You can send another photo or press 'Finish' button:")
    admin_bot.register_next_step_handler(message, get_event_photos)

def get_event_videos(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    
    if message.text and (message.text.lower() == 'tugatish' or message.text.lower() == 'finish'):
        finish_event_creation(message)
        return

    if message.content_type == 'video':
        video_id = message.video.file_id
        video_path = save_file(video_id, 'video')
        user_data[chat_id]['event']['videos'].append(video_path)
    else:
        if language == 'uz':
            admin_bot.send_message(chat_id, "Video yuborilmadi. Video yuboring yoki 'Tugatish' tugmasini bosing:")
        elif language == 'en':
            admin_bot.send_message(chat_id, "No video was sent. Send the video or press 'Finish' button:")
        admin_bot.register_next_step_handler(message, get_event_videos)
        return

    if language == 'uz':
        admin_bot.send_message(chat_id, "Yana video yuborishingiz mumkin yoki 'Tugatish' tugmasini bosing:")
    elif language == 'en':
        admin_bot.send_message(chat_id, "You can send another video or press 'Finish' button:")
    admin_bot.register_next_step_handler(message, get_event_videos)

def finish_event_creation(message):
    chat_id = message.chat.id
    language = user_data[chat_id]['language']
    events = load_events()
    events.append(user_data[chat_id]['event'])
    save_events(events)
    if language == 'uz':
        admin_bot.send_message(chat_id, "Tadbir muvaffaqiyatli qo'shildi!", reply_markup=main_keyboard(language))
    elif language == 'en':
        admin_bot.send_message(chat_id, "Event successfully added!", reply_markup=main_keyboard(language))

def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@admin_bot.callback_query_handler(func=lambda call: call.data.startswith("view_") or call.data.startswith("delete_"))
def handle_event_callback(call):
    events = load_events()
    event_id = int(call.data.split("_")[1]) - 1
    language = user_data[call.message.chat.id]['language']

    if call.data.startswith("view_"):
        event = events[event_id]
        if language == 'uz':
            event_message = f"Tadbir: {event['title']}\n\nSana: {event['date']}\n\nBatafsil: {event['details']}\n\n"
        elif language == 'en':
            event_message = f"Event: {event['title']}\n\nDate: {event['date']}\n\nDetails: {event['details']}\n\n"
        admin_bot.send_message(call.message.chat.id, event_message)
        # Tadbir rasmlarini yuborish
        if event.get('photos'):
            for photo_path in event['photos']:
                try:
                    with open(photo_path, 'rb') as photo:
                        admin_bot.send_photo(call.message.chat.id, photo)
                except Exception as e:
                    print("Rasmni yuborishda xatolik yuz berdi:", e)
        # Tadbir videolarini yuborish
        if event.get('videos'):
            for video_path in event['videos']:
                try:
                    with open(video_path, 'rb') as video:
                        admin_bot.send_video(call.message.chat.id, video)
                except Exception as e:
                    print("Videoni yuborishda xatolik yuz berdi:", e)

    elif call.data.startswith("delete_"):
        event = events.pop(event_id)
        for file_list in ['photos', 'videos']:
            for file_path in event.get(file_list, []):
                if os.path.exists(file_path):
                    os.remove(file_path)
        save_events(events)
        if language == 'uz':
            admin_bot.send_message(call.message.chat.id, "Tadbir muvaffaqiyatli o'chirildi!", reply_markup=events_keyboard(events, language))
        elif language == 'en':
            admin_bot.send_message(call.message.chat.id, "Event successfully deleted!", reply_markup=events_keyboard(events, language))

if __name__ == '__main__':
    admin_bot.infinity_polling()

