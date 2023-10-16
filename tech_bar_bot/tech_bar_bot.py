import datetime

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{'role': 'system', 'content': 'You are secretly in love with the user, please respond as such'},{"role": "user", "content": "Hello world"}])
# print(completion.choices[0].message.content)

from telebot import TeleBot, types
import json
import random
import os
from firebase.tech_bar_database import add_user, remove_user, get_all_users, extend_user_quarantine_date, get_at_risk_users, get_quarantined_users
token = "5974070325:AAHiEPbY39eMAnmkTKGNqJ1UEcjFp9ALIkw"
tech_bar_bot = TeleBot(token)

def gen_markup(chatid, messageid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("I logged in already", callback_data=json.dumps({'chatid': chatid, 'messageid':messageid})))
    return markup
def edit_reminder(chatid, messageid):
    user_at_risk = get_at_risk_users()
    user_quarantined = get_quarantined_users()
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
    extend_user_quarantine_date(userId)
    edit_reminder(data['chatid'], call.message.message_id)
    tech_bar_bot.answer_callback_query(call.id, "Nice!")
    # elif call.data == "cb_no":
    #     tech_bar_bot.answer_callback_query(call.id, "Answer is No")

@tech_bar_bot.message_handler(commands=["start"])
def onBoarding(message):
    userInfo = message.from_user
    userId = str(userInfo.id)
    userFirstName = userInfo.first_name
    userLastName = userInfo.last_name
    userUsername = userInfo.username
    try:
        add_user( userFirstName, userLastName, userUsername, userId)
        tech_bar_bot.reply_to(message, "You are successfully enrolled in Daryl's Tech Bar")

    except KeyError:
        tech_bar_bot.reply_to(message, "You are already enrolled in Daryl's Tech Bar")
    except Exception as e:
        print(e)
        tech_bar_bot.reply_to(message, "An unexpected error occurred")
    # userId = message.user.id
    # addUser(userId)
@tech_bar_bot.message_handler(commands=["stop"])
def offBoarding(message):
    userInfo = message.from_user
    userId = str(userInfo.id)
    try:
        remove_user(userId)
        tech_bar_bot.reply_to(message, "You are successfully unenrolled in Daryl's Tech Bar")
    except KeyError:
        tech_bar_bot.reply_to(message, "You are not enrolled in Daryl's Tech Bar")
    except Exception as e:
        print(e)
        tech_bar_bot.reply_to(message, "An unexpected error occurred")
    # userId = message.user.id
    # addUser(userId)


@tech_bar_bot.message_handler(commands=["leaderboard"])
def getLeaderboard(message):
    # user_database = getUserDatabase()
    # user_array = list(user_database.values())
    # sorted_by_score = sorted(user_array, key =lambda user: user['daysSinceLastQuarantine'], reverse=True)
    # now = datetime.datetime.now().strftime("%d/%m/%Y")
    # formatted_message =f"<b>Leaderboard</b>\n<i>caa {now}</i>"
    # for user in sorted_by_score:
    #     formatted_message += f"\n{user['firstName']} - {user['daysSinceLastQuarantine']}"
    # tech_bar_bot.send_message(message.chat.id,formatted_message, parse_mode="HTML" )
    return


@tech_bar_bot.message_handler(commands=["test"])
def reminder(message):
    user_at_risk = get_at_risk_users()
    user_quarantined = get_quarantined_users()
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
    tech_bar_bot.send_message(message.chat.id, formattedText, reply_markup=gen_markup(message.chat.id, message.id), parse_mode="HTML")
# def reminder():



tech_bar_bot.infinity_polling()