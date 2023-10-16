import datetime

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{'role': 'system', 'content': 'You are secretly in love with the user, please respond as such'},{"role": "user", "content": "Hello world"}])
# print(completion.choices[0].message.content)
from flask import Blueprint, request
from telebot import TeleBot, types
import json
import random
import os
from firebase.tech_bar_database import add_user, remove_user, get_all_users, extend_user_quarantine_date, get_at_risk_users, get_quarantined_users, get_leaderboard, getChats, init_tech_bar, StatusCodes
token = "5974070325:AAHiEPbY39eMAnmkTKGNqJ1UEcjFp9ALIkw"
tech_bar_bot = TeleBot(token)
tech_bar_route = Blueprint('affirmations_routes', __name__)

URL_PREFIX = "techBarBot"
def gen_markup(chatid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("I logged in already", callback_data=json.dumps({
        'callback': 're',
        'chatid': chatid})))
    return markup

def gen_leaderboard_markup(chatid, current):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    if current == "QS":
        markup.add(InlineKeyboardButton("Login Streak", callback_data=json.dumps({
            'callback': 'lb',
            'type': 'LS',
            'chatid': chatid,
        })))
    else:
        markup.add(InlineKeyboardButton("Quarantine Streak", callback_data=json.dumps({
            'callback': 'lb',
            'type': 'QS',
            'chatid': chatid,
        })))
    return markup

def edit_reminder(chatid, messageid):
    user_at_risk = get_at_risk_users(chatid)
    user_quarantined = get_quarantined_users(chatid)
    print(user_at_risk)
    if (len(user_at_risk) + len(user_quarantined)) == 0:
        tech_bar_bot.delete_message(chatid, messageid)
        return
    formattedText = "<b>Reminder to log into GSIB</b>"
    if len(user_at_risk) > 0:
        formattedText += "\n\n<b>Especially</b>"
        for user in user_at_risk:
            formattedText += f"\n@{user['username']}"

    if len(user_quarantined) > 0:
        formattedText += "\n\n<b>Quarantined Users</b>"
        for user in user_quarantined:
            formattedText += f"\n@{user['username']}"
    tech_bar_bot.edit_message_text(formattedText, chatid, messageid)


@tech_bar_bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print(call)
    userId = str(call.from_user.id)
    data = json.loads(call.data)
    if data['callback'] == "lb":
        edit_leaderboard(data['type'], data['chatid'], call.message.message_id)
        tech_bar_bot.answer_callback_query(call.id, "Switching Leaderboard!")
        return
    extend_user_quarantine_date(userId, data['chatid'])
    edit_reminder(data['chatid'], call.message.message_id)
    tech_bar_bot.answer_callback_query(call.id, "Nice!")
    # elif call.data == "cb_no":
    #     tech_bar_bot.answer_callback_query(call.id, "Answer is No")

@tech_bar_bot.message_handler(commands=["join"])
def onBoarding(message):
    userInfo = message.from_user
    userId = str(userInfo.id)
    userFirstName = userInfo.first_name
    userLastName = userInfo.last_name
    userUsername = userInfo.username

    status = add_user(userFirstName, userLastName, userUsername, userId, message.chat.id)
    if status is StatusCodes.OK:
        tech_bar_bot.reply_to(message, "You are successfully enrolled in Daryl's Tech Bar")
    elif status is StatusCodes.GROUP_DOES_NOT_EXIST:
        tech_bar_bot.reply_to(message, "Daryl's Tech Bar is not initialized in this group\n\nUse /start to initialize Daryl's Tech Bar")
    elif status is StatusCodes.USER_EXISTS:
        tech_bar_bot.reply_to(message, "You are already enrolled in Daryl's Tech Bar")
    else:
        tech_bar_bot.reply_to(message, "An unexpected error occurred")

    # userId = message.user.id
    # addUser(userId)
@tech_bar_bot.message_handler(commands=["start"])
def start(message):
    status = init_tech_bar(message.chat.id)
    if status is StatusCodes.OK:
        tech_bar_bot.reply_to(message, "Daryl's Tech Bar successfully initialized\n\nUse /join to join Daryl's Tech Bar")
    elif status is StatusCodes.GROUP_EXISTS:
        tech_bar_bot.reply_to(message, "Daryl's Tech Bar is already initialized in this group\n\nUse /join to join Daryl's Tech Bar")

@tech_bar_bot.message_handler(commands=["stop"])
def offBoarding(message):
    userInfo = message.from_user
    userId = str(userInfo.id)
    status = remove_user(userId, message.chat.id)
    if status is StatusCodes.OK:
        tech_bar_bot.reply_to(message, "You are successfully unenrolled in Daryl's Tech Bar")
    elif status is StatusCodes.GROUP_DOES_NOT_EXIST:
        tech_bar_bot.reply_to(message, "Daryl's Tech Bar is not initialized in this group\n\nUse /start to initialize Daryl's Tech Bar")
    elif status is StatusCodes.USER_DOES_NOT_EXIST:
        tech_bar_bot.reply_to(message, "You are not enrolled in Daryl's Tech Bar")
    else:
        tech_bar_bot.reply_to(message, "An unexpected error occurred")


    # userId = message.user.id
    # addUser(userId)

def edit_leaderboard(type, chatid, messageid):
    login_streak, quarantine_streak = get_leaderboard(chatid)
    if type == "LS":
        formatted_message =f"<b>Leaderboard</b>\n\n<b>Login Streak</b>"
        for user in login_streak:
            formatted_message += f"\n@{user['username']} - {user['login_streak']}"
        tech_bar_bot.edit_message_text(formatted_message, chatid, messageid, parse_mode="HTML", reply_markup=gen_leaderboard_markup(chatid, "LS"))
    elif type == "QS":
        formatted_message =f"<b>Leaderboard</b>\n\n<b>Quarantine Streak</b>"
        for user in quarantine_streak:
            formatted_message += f"\n@{user['username']} - {user['days_since_last_quarantine']}"
        tech_bar_bot.edit_message_text(formatted_message, chatid, messageid, parse_mode="HTML", reply_markup=gen_leaderboard_markup(chatid, "QS"))


@tech_bar_bot.message_handler(commands=["leaderboard"])
def getLeaderboard(message):
    login_streak, quarantine_streak = get_leaderboard(message.chat.id)
    formatted_message =f"<b>Leaderboard</b>\n\n<b>Quarantine Streak</b>"
    for user in quarantine_streak:
        formatted_message += f"\n@{user['username']} - {user['days_since_last_quarantine']}"

    tech_bar_bot.send_message(message.chat.id,formatted_message, parse_mode="HTML" , reply_markup=gen_leaderboard_markup(message.chat.id, 'QS'))
    return


def reminder(chatid):
    user_at_risk = get_at_risk_users(chatid)
    user_quarantined = get_quarantined_users(chatid)
    if (len(user_at_risk) + len(user_quarantined)) == 0:
        return
    formattedText = "<b>Reminder to log into GSIB</b>"
    if len(user_at_risk) > 0:
        formattedText += "\n\n<b>Especially</b>"
        for user in user_at_risk:
            formattedText += f"\n@{user['username']}"



    if len(user_quarantined) > 0:
        formattedText += "\n\n<b>Quarantined Users</b>"
        for user in user_quarantined:
            formattedText += f"\n@{user['username']}"
    tech_bar_bot.send_message(int(chatid), formattedText, reply_markup=gen_markup(chatid), parse_mode="HTML")
# def reminder():

def dailyReminder():
    chatids = getChats()
    print(chatids)
    for chatid in chatids:
        reminder(chatid)



@tech_bar_route.route(f'/{token}', methods = ["POST"])
def getAffirmationMessage():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    tech_bar_bot.process_new_updates([update])
    return "!", 200

@tech_bar_route.route('')
def affirmationWebhook():
    tech_bar_bot.delete_webhook()
    tech_bar_bot.remove_webhook()
    tech_bar_bot.set_webhook(url = f"https://bus-bot.onrender.com/{URL_PREFIX}/" + token)
    return "Webhook set", 200