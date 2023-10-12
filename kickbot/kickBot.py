import os

import telebot
from telebot import types
import time
import datetime
from flask import Blueprint, request

token = os.environ.get('KICK_BOT_TOKEN')
bot = telebot.TeleBot(token)
kickbot_route = Blueprint('kickbot_routes', __name__)
dict = {}
cap = 4
@bot.message_handler(commands=['fku'])
def startKick(msg):
    chatID = msg.chat.id
    targetUser = msg.reply_to_message
    if targetUser is None or targetUser.from_user is None:
        bot.send_message(msg.chat.id, "Kick vote must be started with a reply to the target")
        return
    targetUser = targetUser.from_user
    if str(chatID) not in dict:
        dict[str(chatID)] = {"target": {"username": targetUser.username, "id": targetUser.id}, "votes": []}
        bot.send_message(msg.chat.id, f"Kick vote started for {targetUser.username}")
    else:
        bot.send_message(msg.chat.id, f"Vote already started for {dict[str(chatID)]['target']['username']}")



@bot.message_handler(commands=['kick'])
def kick(msg):
    user = msg.from_user.username
    try :
        data = dict[str(msg.chat.id)]
    except KeyError:
        bot.send_message(msg.chat.id, "Vote not started here")
    if user not in data["votes"]:
        data["votes"].append(user)
        print(dict)
        bot.reply_to(msg, f"good choice! there are now {len(data['votes'])} votes")
    else:
        bot.reply_to(msg, f"you have already voted")
    bot.send_message(msg.chat.id, f"{cap - len(data['votes'])} votes needed to kick")
    if len(data['votes']) >= cap:
        bot.send_message(msg.chat.id, "minimum votes reached!! YEEEEHAWWW")
        print(msg.chat.id)
        dict.pop(str(msg.chat.id))
        bot.kick_chat_member(msg.chat.id, data["target"]["id"])


@bot.message_handler(commands=['set'])
def kick(msg):
    global cap
    cap = int(msg.text.replace("/set", ""))
    bot.send_message(msg.chat.id, f"Vote cap set to {cap}")


@kickbot_route.route(f'/{token}', methods = ["POST"])
def getAffirmationMessage():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@kickbot_route.route('')
def affirmationWebhook():
    bot.delete_webhook()
    bot.remove_webhook()
    bot.set_webhook(url = "https://bus-bot.onrender.com/kickBot/" + token)
    return "Webhook set", 200