from telebot import TeleBot, types
import json
import random
import os
from flask import Blueprint, request
affirmations_token = os.environ.get("AFFIRMATION_BOT_TOKEN")
affirmations_bot = TeleBot(affirmations_token)
affirmations_bot_route = Blueprint('affirmations_routes', __name__)
@affirmations_bot.message_handler(commands=["start", "help"])
def start(message):
    affirmations_bot.send_message(message.chat.id, "hi")
    with open("./affirmations.json", 'r') as f:
        array = json.loads(f.read())
        length = len(array)
        rand = random.randint(0, length - 1)
        affirmations_bot.send_message(message.chat.id, array[rand])

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