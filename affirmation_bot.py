from telebot import TeleBot, types
import json
import random
import os

affirmations_token = os.environ.get("AFFIRMATION_BOT_TOKEN")
affirmations_bot = TeleBot("6358296608:AAF4kwSdV0wp__fvA8ppB74KB_EPdOGDspI")

@affirmations_bot.message_handler(commands=["start", "help"])
def start(message):
    with open("affirmations.json", 'r') as f:
        array = json.loads(f.read())
        length = len(array)
        rand = random.randint(0, length - 1)
        affirmations_bot.send_message(message.chat.id, array[rand])

