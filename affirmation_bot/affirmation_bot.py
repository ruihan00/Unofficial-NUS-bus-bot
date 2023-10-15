from telebot import TeleBot, types
import json
import random
import os
from flask import Blueprint, request
from dotenv import load_dotenv
load_dotenv()
from firebase.affirmations_database import add_subscriber, StatusCodes, remove_subscriber, get_all_subscribers
affirmations_token = os.environ.get("AFFIRMATION_BOT_TOKEN")
affirmations_bot = TeleBot(affirmations_token)
affirmations_bot_route = Blueprint('affirmations_routes', __name__)

def getRandomAffirmation():
    with open(f"{os.getcwd()}/affirmation_bot/affirmations.json", 'r') as f:
        array = json.loads(f.read())
        length = len(array)
        rand = random.randint(0, length - 1)
    return array[rand]
@affirmations_bot.message_handler(commands=["start"])
def start(message):

    status = add_subscriber(message.from_user.first_name, message.from_user.last_name, message.chat.id)
    if (status is StatusCodes.OK):
        affirmations_bot.send_message(message.chat.id, f"""Hello {message.from_user.first_name}!
         
Thank you for joining our positive community of daily affirmation enthusiasts. 🙌

Get ready to start your day with a daily dose of inspiration and motivation. 🌞

Starting tomorrow, you'll receive a fresh and uplifting affirmation to brighten your day. 🌈""")
    elif (status is StatusCodes.USER_EXISTS):
        affirmations_bot.send_message(message.chat.id, f"Hello {message.from_user.first_name}! You are already subscribed!")
    else:
        affirmations_bot.send_message(message.chat.id, f"Hello {message.from_user.first_name}! We ran into a unexpected error")

@affirmations_bot.message_handler(commands=["unsub"])
def unsub(message):

    status = remove_subscriber(message.chat.id)
    if (status is StatusCodes.OK):
        affirmations_bot.send_message(message.chat.id, f"""We're sad to see you go, but we understand.

You have been unsubscribed from Daily Affirmations. If you ever decide to come back and receive daily positivity, we'll be here with open arms to welcome you back.

Remember, a positive mindset is just a message away if you ever need it.""")
    elif (status is StatusCodes.USER_DOES_NOT_EXIST):
        affirmations_bot.send_message(message.chat.id, f"Hello {message.from_user.first_name}! You are not yet subscribed!")
    else:
        affirmations_bot.send_message(message.chat.id, f"Hello {message.from_user.first_name}! We ran into a unexpected error")

@affirmations_bot.message_handler(commands=["quote"])
def sendAffirmation(message):
    affirmations_bot.send_message(message.chat.id, getRandomAffirmation())

@affirmations_bot_route.route(f'/{affirmations_token}', methods = ["POST"])
def getAffirmationMessage():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    affirmations_bot.process_new_updates([update])
    return "!", 200

@affirmations_bot_route.route('')
def affirmationWebhook():
    affirmations_bot.delete_webhook()
    affirmations_bot.remove_webhook()
    affirmations_bot.set_webhook(url = "https://bus-bot.onrender.com/affirmationsBot/" + affirmations_token)
    return "Webhook set", 200

def dailyJob():
    subscribers = get_all_subscribers()
    quote = getRandomAffirmation()
    for sub in subscribers:
        affirmations_bot.send_message(sub.chatid, quote)
