import telebot
import requests
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta

TOKEN = '7162630521:AAFShUGiTT8I6oAnaeZmPQ2tBdYdx1QzOoc'
OWM_API_KEY = 'c7ba51e9910025871c28e5f934252831'

bot = telebot.TeleBot(TOKEN)

def create_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(KeyboardButton('🌤 Hozirgi ob-havo'))
    keyboard.add(KeyboardButton('📅 Haftalik ob-havo'))
    keyboard.add(KeyboardButton('🏙 Shahar o\'zgartirish'))
    return keyboard

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Assalomu alaykum! Iltimos, shahar nomini kiriting (masalan: Toshkent, Uzbekistan):", reply_markup=create_keyboard())
    user_data[user_id] = {'state': 'waiting_for_city'}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text

    if text == '🌤 Hozirgi ob-havo':
        if user_id in user_data and 'city' in user_data[user_id]:
            get_current_weather(message, user_data[user_id]['city'])
        else:
            bot.send_message(user_id, "Iltimos, avval shahar nomini kiriting.")
            user_data[user_id] = {'state': 'waiting_for_city'}
    elif text == '📅 Haftalik ob-havo':
        if user_id in user_data and 'city' in user_data[user_id]:
            get_weekly_weather(message, user_data[user_id]['city'])
        else:
            bot.send_message(user_id, "Iltimos, avval shahar nomini kiriting.")
            user_data[user_id] = {'state': 'waiting_for_city'}
    elif text == '🏙 Shahar o\'zgartirish':
        bot.send_message(user_id, "Yangi shahar nomini kiriting (masalan: Toshkent, Uzbekistan):")
        user_data[user_id] = {'state': 'waiting_for_city'}
    elif user_id in user_data and user_data[user_id]['state'] == 'waiting_for_city':
        user_data[user_id]['city'] = text
        user_data[user_id]['state'] = 'city_selected'
        get_current_weather(message, text)
    else:
        bot.send_message(user_id, "Kechirasiz, tushunmadim. Iltimos, klaviaturadagi tugmalardan foydalaning.")

def get_current_weather(message, city):
    user_id = message.from_user.id
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric&lang=uz'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            description = data['weather'][0]['description']
            
            weather_info = (
                f"🏙 Shahar: {city}\n"
                f"🌡 Harorat: {temp}°C\n"
                f"💧 Namlik: {humidity}%\n"
                f"💨 Shamol tezligi: {wind_speed} m/s\n"
                f"☁️ Tavsif: {description}"
            )
            
            bot.send_message(user_id, weather_info, reply_markup=create_keyboard())
        else:
            bot.send_message(user_id, "Kechirasiz, bunday shahar topilmadi. Iltimos, qayta urinib ko'ring.", reply_markup=create_keyboard())
    
    except Exception as e:
        bot.send_message(user_id, "Xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.", reply_markup=create_keyboard())

def get_weekly_weather(message, city):
    user_id = message.from_user.id
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OWM_API_KEY}&units=metric&lang=uz'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            weather_info = f"🏙 {city} uchun haftalik ob-havo ma'lumoti:\n\n"
            
            current_date = None
            for forecast in data['list']:
                forecast_date = datetime.fromtimestamp(forecast['dt'])
                if current_date != forecast_date.date():
                    current_date = forecast_date.date()
                    weather_info += f"\n📅 {current_date.strftime('%d.%m.%Y')}:\n"
                
                if forecast_date.hour in [6, 12, 18]:
                    temp = forecast['main']['temp']
                    humidity = forecast['main']['humidity']
                    wind_speed = forecast['wind']['speed']
                    description = forecast['weather'][0]['description']
                    
                    time_of_day = "🌅" if forecast_date.hour == 6 else "☀️" if forecast_date.hour == 12 else "🌙"
                    
                    weather_info += (
                        f"{time_of_day} {forecast_date.strftime('%H:%M')}: "
                        f"🌡 {temp:.1f}°C, 💧 {humidity}%, 💨 {wind_speed:.1f} m/s\n"
                        f"   ☁️ {description}\n"
                    )
            
            bot.send_message(user_id, weather_info, reply_markup=create_keyboard())
        else:
            bot.send_message(user_id, "Kechirasiz, bunday shahar topilmadi. Iltimos, qayta urinib ko'ring.", reply_markup=create_keyboard())
    
    except Exception as e:
        bot.send_message(user_id, "Xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.", reply_markup=create_keyboard())

bot.polling(none_stop=True)
