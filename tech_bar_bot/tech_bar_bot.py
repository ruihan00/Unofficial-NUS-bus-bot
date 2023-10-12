import datetime

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{'role': 'system', 'content': 'You are secretly in love with the user, please respond as such'},{"role": "user", "content": "Hello world"}])
# print(completion.choices[0].message.content)

from telebot import TeleBot, types
import json
import random
import os

token = "5974070325:AAHiEPbY39eMAnmkTKGNqJ1UEcjFp9ALIkw"
tech_bar_bot = TeleBot(token)
def getUserDatabase():
    with open('./tech_bar_data.json', 'r') as f:
        return json.loads(f.read())
def writeUserDatabase(database):
    with open('./tech_bar_data.json', 'w') as w:
        w.write(json.dumps(database, indent=4))
def getCurrentTime():
    return datetime.datetime.now()

def formatTimeDDMMYY(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%d/%m/%Y")
def strToDatetime(dateString):
    return datetime.datetime.strptime(dateString, "%d/%m/%Y")
def extendQuarantineDate(userId):
    print(f"Extending quarantine date for {userId}")
    user_database = getUserDatabase()
    print(user_database)
    if userId not in user_database:
        print(f"User not found")
        return
    currentDate = user_database[userId]['quarantineDate']
    if not currentDate:
        user_database[userId]['quarantineDate'] = formatTimeDDMMYY(getCurrentTime())
    else:
        currentDateTime = strToDatetime(currentDate)
        user_database[userId]['quarantineDate'] = formatTimeDDMMYY(currentDateTime + datetime.timedelta(days=5))
    print(user_database)
    writeUserDatabase(user_database)

def addUser(userId, firstName, lastName, userName):
    user_database = getUserDatabase()
    print(userId)
    if userId in user_database:

        raise KeyError("User is already in database")
    user_database[userId] = {
        "firstName": firstName,
        "lastName" : lastName,
        "quarantineDate": None,
        "userName": userName,
        "daysSinceLastQuarantine": 0
    }
    writeUserDatabase(user_database)

def removeUser(userId):
    user_database = getUserDatabase()
    if userId in user_database:
        user_database[userId] = None

def gen_markup(chatid, messageid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("I logged in already", callback_data=json.dumps({'chatid': chatid, 'messageid':messageid})))
    return markup



@tech_bar_bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print(call)
    userId = str(call.from_user.id)
    data = json.loads(call.data)
    extendQuarantineDate(userId)
    editReminder(data['chatid'], data['messageid'])
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
        addUser(userId, userFirstName, userLastName, userUsername)
        tech_bar_bot.reply_to(message, "You are successfully enrolled in Daryl's Tech Bar")

    except KeyError:
        tech_bar_bot.reply_to(message, "You are already enrolled in Daryl's Tech Bar")
    except Exception as e:
        print(e)
        tech_bar_bot.reply_to(message, "An unexpected error occurred")
    # userId = message.user.id
    # addUser(userId)
@tech_bar_bot.message_handler(commands=["leaderboard"])
def getLeaderboard(message):
    user_database = getUserDatabase()
    user_array = list(user_database.values())
    sorted_by_score = sorted(user_array, key =lambda user: user['daysSinceLastQuarantine'], reverse=True)
    now = datetime.datetime.now().strftime("%d/%m/%Y")
    formatted_message =f"<b>Leaderboard</b>\n<i>caa {now}</i>"
    for user in sorted_by_score:
        formatted_message += f"\n{user['firstName']} - {user['daysSinceLastQuarantine']}"
    tech_bar_bot.send_message(message.chat.id,formatted_message, parse_mode="HTML" )
@tech_bar_bot.message_handler(commands=["start"])
def onBoarding(message):
    userInfo = message.from_user
    userId = userInfo.id
    userFirstName = userInfo.first_name
    userLastName = userInfo.last_name
    userUsername = userInfo.username
    try:
        addUser(userId, userFirstName, userLastName, userUsername)
        tech_bar_bot.reply_to(message, "You are successfully enrolled in Daryl's Tech Bar")

    except:
        tech_bar_bot.reply_to(message, "You are already enrolled in Daryl's Tech Bar")
def editReminder(chatid, reminderId):
    user_database = getUserDatabase()
    userToRemind = []
    quarantinedUser = []
    for user in user_database.values():
        if not user['quarantineDate']:
            userToRemind.append(user)
            continue
        userQuarantineTime = strToDatetime(user['quarantineDate'])
        if (getCurrentTime() > userQuarantineTime):
            quarantinedUser.append(user)
            continue

        if (getCurrentTime() > userQuarantineTime - datetime.timedelta(days=2)):
            userToRemind.append(user)
    print(userToRemind)
    formattedText = "<b>Reminder to log into GSIB</b>"
    if len(userToRemind) > 0:
        formattedText += "\n\n<b>Especially</b>"
    else:
        tech_bar_bot.delete_message(chatid, reminderId)
        return
    for user in userToRemind:
        formattedText += f"\n@{user['userName']}"
    if len(quarantinedUser) > 0:
        formattedText += "\n\n<b>Quarantined Users</b>"
        for user in quarantinedUser:
            formattedText += f"\n@{user['userName']}"
    tech_bar_bot.edit_message_text(chatid, reminderId, formattedText)
@tech_bar_bot.message_handler(commands=["test"])
def reminder(message):
    print(message.chat)
    user_database = getUserDatabase()
    userToRemind = []
    quarantinedUser = []
    for user in user_database.values():
        if not user['quarantineDate']:
            userToRemind.append(user)
            continue
        userQuarantineTime = strToDatetime(user['quarantineDate'])
        if (getCurrentTime() > userQuarantineTime):
            quarantinedUser.append(user)
            continue

        if (getCurrentTime() > userQuarantineTime - datetime.timedelta(days=2)):
            userToRemind.append(user)
    print(userToRemind)
    formattedText = "<b>Reminder to log into GSIB</b>"
    if len(userToRemind) > 0:
        formattedText += "\n\n<b>Especially</b>"
    else:
        return
    for user in userToRemind:
        formattedText += f"\n@{user['userName']}"
    if len(quarantinedUser) > 0:
        formattedText += "\n\n<b>Quarantined Users</b>"
        for user in quarantinedUser:
            formattedText += f"\n@{user['userName']}"
    tech_bar_bot.send_message(message.chat.id, formattedText, reply_markup=gen_markup(message.chat.id, message.id), parse_mode="HTML")
# def reminder():



tech_bar_bot.infinity_polling()