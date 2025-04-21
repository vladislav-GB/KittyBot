import os
from dotenv import load_dotenv
import requests
from telebot import TeleBot, types
import random
from apscheduler.schedulers.background import BackgroundScheduler  # Новый импорт

load_dotenv()
secret_token = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
bot = TeleBot(token=secret_token)
URL = 'https://api.thecatapi.com/v1/images/search'

cat_phrases = [
    "Держи котика! 🐱",
    "Вот тебе пушистый друг 😸",
    "Няшный кот прибыл! 😻",
    "Смотри, какая прелесть! 😺",
    "Еще один котик для тебя! 🐾",
    "Пушистый сюрприз! 🎁",
    "Этот кот точно поднимет тебе настроение 🐈",
    "Котик прибыл по заказу! 📦",
    "Котогенератор активирован! 🚀",
    "Лови мурлыку! 🐾"
]

def get_new_image():
    response = requests.get(URL).json()
    random_cat = response[0].get('url')
    return random_cat


def send_scheduled_cat():
    bot.send_photo(CHAT_ID, get_new_image())
    bot.send_message(CHAT_ID, text='Твой вечерний котик перед сном пришел к тебе!')

scheduler = BackgroundScheduler()
scheduler.add_job(send_scheduled_cat, 'cron', hour=22, minute=30)  
scheduler.start()

@bot.message_handler(commands=['newcat'])
@bot.message_handler(func=lambda message: message.text == 'Еще котик!')
def new_cat(message):
    chat = message.chat
    bot.send_photo(chat.id, get_new_image())
    bot.send_message(chat.id, random.choice(cat_phrases))

@bot.message_handler(commands=['start'])
def wake_up(message):
    chat = message.chat
    name = message.chat.first_name
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_newcat = types.KeyboardButton('Еще котик!')  
    keyboard.add(button_newcat)

    bot.send_message(
        chat_id=chat.id,
        text=f'Привет, {name}! Посмотри, какого котика я тебе нашёл)',
        reply_markup=keyboard,
    )
    bot.send_photo(chat.id, get_new_image())

@bot.message_handler(content_types=['text'])
def say_hi(message):
    chat = message.chat
    chat_id = chat.id
    bot.send_message(chat_id=chat_id, text='Привет, я KittyBot!')

bot.polling()