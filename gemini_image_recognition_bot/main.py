import telebot
import base64
import os
from flask import Blueprint, request
from telebot import types
from gemini_image_recognition_bot.image_recognition import extract_injury_details, extract_user_details
import requests
API_TOKEN = os.environ.get('GEMINI_TOKEN')
GEMINI_URL_PREFIX = "geminiimagerec"
bot = telebot.TeleBot(API_TOKEN)
gemini_img_route = Blueprint('gemini_img_route', __name__)


# Global variable to store user details
user_details = {}
def genStartMarkup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.one_time_keyboard = True
    markup.add(types.InlineKeyboardButton('Report a incident', callback_data='report'))
    markup.add(types.InlineKeyboardButton('Learn more', url="https://www.mom.gov.sg/workplace-safety-and-health/work-accident-reporting"))

    return markup

def genInjuryMarkup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.one_time_keyboard = True
    markup.add(types.InlineKeyboardButton('Confirm', callback_data='confirm_injury'))
    markup.add(types.InlineKeyboardButton('Change injury description', callback_data='change_injury'))

    return markup
def genInjuredPersonPhotoIdChoiceMarkup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.one_time_keyboard = True
    markup.add(types.InlineKeyboardButton('Photo ID', callback_data='ip_photo_id'))
    markup.add(types.InlineKeyboardButton('Manual', callback_data='ip_manual'))
    return markup

def genIPManualMarkup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.one_time_keyboard = True
    markup.add(types.InlineKeyboardButton('Enter manually', callback_data='ip_manual'))

    return markup

def genReporterChoiceMarkup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.one_time_keyboard = True
    markup.add(types.InlineKeyboardButton('Photo ID', callback_data='reporter_photo_id'))
    markup.add(types.InlineKeyboardButton('Manual', callback_data='reporter_manual'))
    return markup

def genReporterManualMarkup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.one_time_keyboard = True
    markup.add(types.InlineKeyboardButton('Enter manually', callback_data='reporter_manual'))

    return markup


def genConfirmLocationMarkup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.one_time_keyboard = True
    markup.add(types.InlineKeyboardButton('Confirm', callback_data='confirm_location'))
    markup.add(types.InlineKeyboardButton('Change location', callback_data='change_location'))
    return markup

def genFinalSubmissionMarkup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.one_time_keyboard = True
    markup.add(types.InlineKeyboardButton('Submit', callback_data='final'))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
                     """Hello! I am here to assist you in reporting your workplace incident to the Ministry of Manpower.\n
I am a PROOF of CONCEPT, so if my responses are slow I would like to be sorry to keep you waiting.
""", reply_markup=genStartMarkup())
    # bot.send_message(message.chat.id, "To start the process, send me a photo ID image.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'report':
        bot.send_message(str(call.message.chat.id), """Oh no! Please make sure you attend to the injury first!\n
If you are ready to report, please send me a picture of the injured person with the injury visibly shown.""")
        user_details[str(call.message.chat.id)] = {
            'injury_details': '',
            'injured_person_name': '',
            'injured_person_dob': '',
            'injured_person_id': '',
            'reporter_name': '',
            'reporter_id': '',
            'location': '',           
        }
        bot.register_next_step_handler(call.message, handle_injury_image)

    elif call.data == 'Yes':
        bot.send_message(call.message.chat.id, "Great! Now, please send me an image of the injury.")
    elif call.data == 'confirm_injury':
        bot.send_message(call.message.chat.id, "Excellent! Next, I will need the details of the injured person", reply_markup=genInjuredPersonPhotoIdChoiceMarkup())
    elif call.data == 'change_injury':
        bot.send_message(call.message.chat.id, "Please enter the correct injury details.")
        bot.register_next_step_handler(call.message, change_injury_details)
    elif call.data == 'ip_photo_id':
        bot.send_message(call.message.chat.id, "Please send me a photo ID image.")
        bot.register_next_step_handler(call.message, handleIPPhotoId)
    elif call.data == 'ip_manual':
        send_IP_confirmation_message(call.message.chat.id)
    elif call.data == 'change_ip_name':
        bot.send_message(call.message.chat.id, "Please enter the name of the injured person.")
        bot.register_next_step_handler(call.message, change_ip_name)
    elif call.data == 'change_ip_dob':
        bot.send_message(call.message.chat.id, "Please enter the date of birth of the injured person.")
        bot.register_next_step_handler(call.message, change_ip_dob)
    elif call.data == 'change_ip_id_number':
        bot.send_message(call.message.chat.id, "Please enter the ID number of the injured person.")
        bot.register_next_step_handler(call.message, change_ip_id_number)
    elif call.data == 'confirm_ip':
        bot.send_message(call.message.chat.id, "Great! Now i will need your details!", reply_markup=genReporterChoiceMarkup())
    elif call.data == 'reporter_photo_id':
        bot.send_message(call.message.chat.id, "Please send me a photo ID image.")
        bot.register_next_step_handler(call.message, handleReporterPhotoId)
    elif call.data == 'change_reporter_name':
        bot.send_message(call.message.chat.id, "Please enter your name.")
        bot.register_next_step_handler(call.message, change_reporter_name)
    elif call.data == 'change_reporter_id_number':
        bot.send_message(call.message.chat.id, "Please enter your ID number.")
        bot.register_next_step_handler(call.message, change_reporter_id_number)
    elif call.data == 'reporter_manual':
        send_reporter_confirmation_message(call.message.chat.id)
    elif call.data == 'confirm_reporter':
        bot.send_message(call.message.chat.id, "Great! Now, I will need the location of the incident.")
        bot.register_next_step_handler(call.message, handle_location)
    elif call.data == 'change_location':
        bot.send_message(call.message.chat.id, "Please enter the location of the incident.")
        bot.register_next_step_handler(call.message, handle_location)
    elif call.data == 'confirm_location':
         handle_final_submission(call.message)
    elif call.data == 'final':
        bot.send_message(call.message.chat.id, "Your injury report has been submitted to the Ministry of Manpower. Thank you for using our service!")
        bot.edit_message_reply_markup(call.message.chat.id, reply_markup=None, message_id=call.message.message_id)
        bot.answer_callback_query(call.id, "Great! I have submitted the details", show_alert=True)
        return
    bot.answer_callback_query(call.id, "Got it!")
    bot.edit_message_reply_markup(call.message.chat.id, reply_markup=None, message_id=call.message.message_id)

def handleIPPhotoId(photo):
    try:
        fileid = photo.photo[-1].file_id
        file = bot.get_file(fileid)
        file_path = file.file_path
        if file.file_path is None:
            bot.send_message(photo.chat.id, "I need to you send me a photo of the injured person's photo ID. Please try again.")
            bot.register_next_step_handler(photo, handleIPPhotoId)
            return
        downloaded_file = bot.download_file(file_path)
        bot.send_message(photo.chat.id, "Processing image... (may take up to 60 seconds)")

    
        # Step 2: Extract details from photo ID image
        name, dob, id_number = extract_user_details(downloaded_file)
        user_details[str(photo.chat.id)]['injured_person_name'] = name
        user_details[str(photo.chat.id)]['injured_person_dob'] = dob
        user_details[str(photo.chat.id)]['injured_person_id'] = id_number

        # Step 3: Confirm details with buttons
        send_IP_confirmation_message(photo.chat.id)
    except Exception as e:
        print(e)
        bot.send_message(photo.chat.id, f"Sorry! I ran into an error processing the image, please send me the image again or click to enter manually", reply_markup=genIPManualMarkup())
        bot.register_next_step_handler(photo, handleIPPhotoId)
        return
    
def send_IP_confirmation_message(chat_id, additional_message=None):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.one_time_keyboard = True
    markup.add(types.InlineKeyboardButton('Confirm', callback_data='confirm_ip'))
    markup.add(types.InlineKeyboardButton('Change name', callback_data='change_ip_name'))
    markup.add(types.InlineKeyboardButton('Change date of birth', callback_data='change_ip_dob'))
    markup.add(types.InlineKeyboardButton('Change ID number', callback_data='change_ip_id_number'))

    details_message = f"Name: {user_details[str(chat_id)]['injured_person_name']}\nDate of Birth: {user_details[str(chat_id)]['injured_person_dob']}\nID Number: {user_details[str(chat_id)]['injured_person_id']}"
    if additional_message:
        details_message += f"\n\n{additional_message}"

    bot.send_message(chat_id, "The details of the injured person is:\n" + details_message, reply_markup=markup)

def change_ip_name(message):
    user_details[str(message.chat.id)]['injured_person_name'] = message.text
    send_IP_confirmation_message(str(message.chat.id), f"Name has been updated to {user_details[str(message.chat.id)]['injured_person_name']}.")

def change_ip_dob(message):
    user_details[str(message.chat.id)]['injured_person_dob'] = message.text
    send_IP_confirmation_message(str(message.chat.id), f"Date of Birth has been updated to {user_details[str(message.chat.id)]['injured_person_dob']}.")

def change_ip_id_number(message):
    user_details[str(message.chat.id)]['injured_person_id'] = message.text
    send_IP_confirmation_message(str(message.chat.id), f"ID Number has been updated to {user_details[str(message.chat.id)]['injured_person_id']}.")


def handleReporterPhotoId(photo):
    try:
        fileid = photo.photo[-1].file_id
        file = bot.get_file(fileid)
        file_path = file.file_path
        if file.file_path is None:
            bot.send_message(photo.chat.id, "I need to you send me a photo of the reporter's photo ID. Please try again.")
            bot.register_next_step_handler(photo, handleReporterPhotoId)
            return
        downloaded_file = bot.download_file(file_path)
        bot.send_message(photo.chat.id, "Processing image... (may take up to 60 seconds)")

    
        # Step 2: Extract details from photo ID image
        name, id_number, dob = extract_user_details(downloaded_file)
        user_details[str(photo.chat.id)]['reporter_name'] = name
        user_details[str(photo.chat.id)]['reporter_id'] = id_number
        # Step 3: Confirm details with buttons
        send_reporter_confirmation_message(photo.chat.id)
    except Exception as e:
        print(e)
        bot.send_message(photo.chat.id, f"Sorry! I ran into an error processing the image, please send me the image again or click to enter manually", reply_markup=genReporterManualMarkup())
        return

def send_reporter_confirmation_message(chat_id, additional_message=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Confirm', callback_data='confirm_reporter'))
    markup.add(types.InlineKeyboardButton('Change name', callback_data='change_reporter_name'))
    markup.add(types.InlineKeyboardButton('Change ID number', callback_data='change_reporter_id_number'))

    details_message = f"Name: {user_details[str(chat_id)]['reporter_name']}\nID Number: {user_details[str(chat_id)]['reporter_id']}"
    if additional_message:
        details_message += f"\n\n{additional_message}"

    bot.send_message(chat_id, "Your details are:\n" + details_message, reply_markup=markup)

def change_reporter_name(message):
    user_details[str(message.chat.id)]['reporter_name'] = message.text
    send_reporter_confirmation_message(str(message.chat.id), f"Name has been updated to {user_details[str(message.chat.id)]['reporter_name']}.")
def change_reporter_id_number(message):
    user_details[str(message.chat.id)]['reporter_id'] = message.text
    send_reporter_confirmation_message(str(message.chat.id), f"ID Number has been updated to {user_details[str(message.chat.id)]['reporter_id']}.")


# Step 5: Ask for injury image
def handle_injury_image(message):
    try:
        fileid = message.photo[-1].file_id
        file = bot.get_file(fileid)
        file_path = file.file_path
        if file.file_path is None:
            bot.send_message(message.chat.id, "I need to you send me a photo of the injury. Please try again.")
            bot.register_next_step_handler(message, handle_injury_image)
            return
        bot.send_message(message.chat.id, "Processing injury image... (may take up to 60 seconds)")
        downloaded_file = bot.download_file(file_path)

    
        # Step 6: Extract details from injury image
        details = extract_injury_details(downloaded_file)
        print(details)
        user_details[str(message.chat.id)]['injury_details'] = details

        # Step 7: Confirm details with buttons
        send_injury_confirmation_message(message.chat.id)
    except Exception as e:
        print(message.chat.id)
        print(e)
        bot.send_message(message.chat.id, f"Sorry! I ran into an error processing the image, please send me the image again.")
        bot.register_next_step_handler(message, handle_injury_image)
        return
    
def send_injury_confirmation_message(chat_id, additional_message=None):
    details_message = f"Injury Details:\n{user_details[str(chat_id)]['injury_details']}"
    if additional_message:
        details_message += f"\n\n{additional_message}"

    bot.send_message(chat_id, details_message, reply_markup=genInjuryMarkup())


def change_injury_details(message):
    user_details[str(message.chat.id)]['injury_details'] = message.text
    send_injury_confirmation_message(str(message.chat.id))


def handle_location(message):
    if message.location is None:
        user_details[str(message.chat.id)]['location'] = message.text
        confirm_location(message)
        return
    userLat = message.location.latitude
    userLong = message.location.longitude
    res = requests.get(f"https://geocode.maps.co/reverse?lat={userLat}&lon={userLong}&api_key={os.getenv('GEO_CODE_KEY')}")
    if res.status_code == 200:
        data = res.json()
        user_details[str(message.chat.id)]['location'] = data['display_name']
        confirm_location(message)
    else:
        bot.send_message(message.chat.id, "Sorry, I ran into an error. Please try again.")
        bot.register_next_step_handler(message, handle_location)


def confirm_location(message):
    bot.send_message(message.chat.id, f"Heres the location i got!\n {user_details[str(message.chat.id)]['location']}", reply_markup=genConfirmLocationMarkup())


def handle_final_submission(message):
    bot.send_message(message.chat.id, f"""
Alright! Here's a summary of the details you've provided:
                     
<b>Injury Details:</b> {user_details[str(message.chat.id)]['injury_details']}


<b>Injured Person's Name:</b> {user_details[str(message.chat.id)]['injured_person_name']}

<b>Injured Person's Date of Birth:</b> {user_details[str(message.chat.id)]['injured_person_dob']}

<b>Injured Person's ID Number:</b> {user_details[str(message.chat.id)]['injured_person_id']}


<b>Reporter's Name:</b> {user_details[str(message.chat.id)]['reporter_name']}

<b>Reporter's ID Number:</b> {user_details[str(message.chat.id)]['reporter_id']}

<b>Location of Incident:</b> {user_details[str(message.chat.id)]['location']}
""", reply_markup=genFinalSubmissionMarkup(), parse_mode='html')
    

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

