import os
import random
import requests
from dotenv import load_dotenv
from telebot import TeleBot, types
from apscheduler.schedulers.background import BackgroundScheduler


load_dotenv()
secret_token = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
bot = TeleBot(token=secret_token)

CAT_API_URL = 'https://api.thecatapi.com/v1/images/search'
CATAAS_GIF_URL = 'https://cataas.com/cat/gif'
BREED_BLACKLIST = ['bsho']  # British Shorthair

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

cat_memes = [
    "Лови котомем! 😹",
    "Пушистый дурында! 😼",
    "Котомем! 🐈"
]


def get_cat_image():
    """Fetch a random cat image URL from The Cat API, excluding blacklisted breeds."""
    breeds = requests.get('https://api.thecatapi.com/v1/breeds').json()
    allowed_breeds = [
        breed['id'] for breed in breeds
        if breed['id'] not in BREED_BLACKLIST
    ]
    breed_id = random.choice(allowed_breeds)
    response = requests.get(CAT_API_URL, params={'breed_ids': breed_id}).json()
    return response[0].get('url')


def get_cat_gif():
    """Fetch a random cat GIF URL from CATAAS with cache-busting parameter."""
    return f'{CATAAS_GIF_URL}?{random.randint(0, 999999)}'


def send_scheduled_cat():
    """Send scheduled evening cat image to the predefined chat."""
    bot.send_photo(CHAT_ID, get_cat_image())
    bot.send_message(
        CHAT_ID,
        text='Твой вечерний котик перед сном пришел к тебе!🐈'
    )


def send_morning_cat():
    """Send scheduled morning cat GIF to the predefined chat."""
    bot.send_animation(
        CHAT_ID,
        get_cat_gif(),
        caption='Утренний котик для чубзика!🐾'
    )


scheduler = BackgroundScheduler()
scheduler.add_job(send_scheduled_cat, 'cron', hour=22, minute=0)
scheduler.add_job(send_morning_cat, 'cron', hour=8, minute=0)
scheduler.start()


@bot.message_handler(commands=['start'])
def wake_up(message):
    """Handle /start command and send welcome message with first cat."""
    name = message.chat.first_name
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_newcat = types.KeyboardButton('Еще котик!')
    button_gif = types.KeyboardButton('КотоМем')
    keyboard.add(button_newcat, button_gif)

    bot.send_message(
        chat_id=message.chat.id,
        text=f'Привет, {name}! Посмотри, какого котика я тебе нашёл)',
        reply_markup=keyboard,
    )
    bot.send_photo(message.chat.id, get_cat_image())


@bot.message_handler(func=lambda message: message.text == 'Еще котик!')
def new_cat(message):
    """Send new cat image when 'Еще котик!' button is pressed."""
    bot.send_photo(message.chat.id, get_cat_image())
    bot.send_message(message.chat.id, random.choice(cat_phrases))


@bot.message_handler(func=lambda message: message.text == 'КотоМем')
def send_gif(message):
    """Send cat GIF when 'КотоМем' button is pressed."""
    bot.send_animation(
        message.chat.id,
        get_cat_gif(),
        caption=random.choice(cat_memes)
    )


@bot.message_handler(content_types=['text'])
def say_hi(message):
    """Handle any text message with instructions."""
    bot.send_message(
        chat_id=message.chat.id,
        text='Привет, я KittyBot! Используй кнопки ниже чтобы получать котиков!')


bot.polling()
