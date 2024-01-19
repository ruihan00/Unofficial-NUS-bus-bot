import telebot
import base64
from gemini_image_recognition_bot.image_recognition import recognise_image
import os
from flask import Blueprint, request
from telebot import types

API_TOKEN = os.environ.get('GEMINI_TOKEN')
GEMINI_URL_PREFIX = "geminiimagerec"
bot = telebot.TeleBot(API_TOKEN)
gemini_img_route = Blueprint('gemini_img_route', __name__)

@bot.message_handler(content_types=['photo'])
def handlePhoto(photo):
    fileid = photo.photo[-1].file_id
    print(fileid)
    file = bot.get_file(fileid)
    file_path = file.file_path
    downloaded_file = bot.download_file(file_path)
    bot.send_message(photo.chat.id, "Processing image... (may take up to 10 seconds)")

    with open(f'${fileid}.jpg','wb') as new_file:
        new_file.write(downloaded_file)
    try:
        result = recognise_image(f'${fileid}.jpg')
    except Exception as e:
        bot.send_message(photo.chat.id, f"Error processing image: {e}")
        return
    prediction = result.candidates[0].content.parts[0].text.strip()
    bot.send_message(photo.chat.id, "This image shows: \n" + prediction)
    os.remove(f'${fileid}.jpg')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello i am here to assist in injury reporting, send me a photo of a injury and i will let you know what kind of injury it is to the best of my ability!")

@gemini_img_route.route(f'/{API_TOKEN}', methods = ["POST"])
def getImageRequest():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@gemini_img_route.route('')
def geminiWebhook():
    bot.delete_webhook()
    bot.remove_webhook()
    bot.set_webhook(url = "https://bus-bot.onrender.com/geminiimagerec/" + API_TOKEN)
    return API_TOKEN, 200
