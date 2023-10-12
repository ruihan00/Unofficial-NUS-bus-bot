import random
import re

import telebot
import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

token = "5647420285:AAGoC80NXny7nH0ElcYuLcumPHxfe1gF-z4"
bot = telebot.TeleBot(token)
dict = {}
cap = 1
activeWhineMode = False
activeFlameMode = False
activeCancelMode = False
activeNavinMode = False
count = 0
startTime = datetime.datetime.now()
replyChance = 10
NO_STICKER = "CAACAgUAAxkBAAIBKGN4fZKu-h1d4bHK4NQBJmyeoz39AAJwBwACwDSZVSt3aa7siG4_KwQ"
FLAMES = ['your mom',
          'fuck off',
          'no',
          'yes just not w u',
          'wtf',
          '-.-',
          'keep dreaming',
          'gay',
          'your mom gay',
          'no wonder u single',
          'dont be a whiny bitch',
          'stop whining',
          'shut up',
          'omg just fucking shut up',
          'is it possible for you to be anymore annoying',
          'oh boo fucking hoo',
          'k',
          'ok try harder',
          "Why are you gay",
          "Fking Simp."]

WHINES = ['huhhhhhhh u not freeeeeeee??? *weird navin face*',
          'but.. but.. but.. but...',
          'i need new friends *sad face*',
          'help lahhhhhh',
          'huh ur name got no ro???',
          'breakfast anyone.. :(((',
          'wlaoooooo',
          'hnnnnnnggggggggggg',
          'Im not a simpppppp',
          "I want to hangout with herrrrrrr",
          "I miss herrrrrr",
          "Why is she not replyinggggg"]

NAVIN_SIMULATION = ["i am always sad",
                    "i am super gay",
                    "i am the low budget version of scruffy rat",
                    "i add letters for nooooooo reasonnnnnnn",
                    "i type like a 14 y/o",
                    "i can’t take photos like a regular person because it takes me 20 years to fix my hair",
                    "gotta dip!",
                    "my physics friends think im hilarious!",
                    "sorry too busy simping",
                    "don’t mind me, just going to delete some messages",
                    "i looooooooooove chs",
                    "i once went on a pretend date with my friend",
                    "omg guys! i have sister issues!!!!!",
                    "i can hold 2 ml of alcohol",
                    "i sleep during movies",
                    "i overshare about my life to everybody who’ll listen",
                    "i think the world’s best matchmaker is the gossip girl",
                    "whyyyyyyyyyyy",
                    "Being evergreen is taking a toll on me",
                    "Caitlin is so funnyyy",
                    "I want to date caitlin",
                    "GEA1000N is so muchh harderrrr"]


def getRandom(arr):
    length = len(arr) - 1
    global count
    count += 1
    return arr[random.randint(0, length)]


def genStartMarkup():
    markup = InlineKeyboardMarkup()
    if not activeCancelMode and not activeFlameMode and not activeWhineMode and not activeNavinMode:
        markup.add(InlineKeyboardButton("Flame Mode", callback_data="flame"))
        markup.add(InlineKeyboardButton("Whine Mode", callback_data="whine"))
        markup.add(InlineKeyboardButton("Navin Simulation Mode", callback_data="navin"))
        markup.add(InlineKeyboardButton("Cancel Mode", callback_data="cancel"))
    else:
        markup.add(InlineKeyboardButton("Stop Mode", callback_data="stop"))
    return markup


def isNavin(id):
    return id == 1101502447


def haveMode():
    if activeFlameMode:
        return "Flame Mode"
    if activeWhineMode:
        return "Whine Mode"
    if activeCancelMode:
        return "Cancel Mode"
    if activeNavinMode:
        return "Navin Simulation Mode"
    return None


@bot.callback_query_handler(func=lambda call: True)
def activateMode(call):
    mode = call.data
    if isNavin(call.message.from_user.id):
        bot.send_sticker(call.message.chat.id, NO_STICKER)
        return
    if mode == "stop":
        bot.answer_callback_query(call.id, f"{haveMode()} deactivated")
        stopMode(call.message.chat.id)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=genStartMarkup())
        return
    if haveMode() is not None:
        bot.send_message(call.message.chat.id, f"There is already a active mode: {haveMode()}")
        bot.answer_callback_query(call.id, f"There is already a active mode: {haveMode()}")
        return
    if mode == "flame":
        flameMode(call.message.chat.id)
        bot.answer_callback_query(call.id, "Flame Mode Activated")
    if mode == "whine":
        whineMode(call.message.chat.id)
        bot.answer_callback_query(call.id, "Whine Mode Activated")
    if mode == "navin":
        navinMode(call.message.chat.id)
        bot.answer_callback_query(call.id, "Navin Simulation Mode Activated")
    if mode == "cancel":
        # cancelMode(call.message.chat.id)
        bot.answer_callback_query(call.id, "Coming Soon")

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=genStartMarkup())


def navinMode(chatID):
    global activeNavinMode
    activeNavinMode = True
    bot.send_message(chatID, "Navin Simulation Mode activated")
    bot.register_next_step_handler_by_chat_id(chatID, navinSimulateNextMessage)


def navinSimulateNextMessage(msg):
    if not activeNavinMode:
        return

    text = msg.text
    if text == "/stop":
        stopMode(msg.chat.id)
        return
    if text == "/start":
        bot.send_message(msg.chat.id, "Select a mode", reply_markup=genStartMarkup())
        return
    if text == "/status":
        status(msg)
        return
    if text == "/chance":
        setChance(msg)
        return
    if random.randint(1, 10) > replyChance:
        bot.register_next_step_handler_by_chat_id(msg.chat.id, navinSimulateNextMessage)
        return
    if not isNavin(msg.from_user.id):
        bot.send_message(msg.chat.id, getRandom(NAVIN_SIMULATION))

    bot.register_next_step_handler_by_chat_id(msg.chat.id, navinSimulateNextMessage)


def cancelMode(chatID):
    global activeCancelMode
    activeCancelMode = True
    bot.send_message(chatID, "Cancel Mode activated")


def whineMode(chatID):
    global activeWhineMode
    activeWhineMode = True
    bot.send_message(chatID, "Whine Mode activated")
    bot.register_next_step_handler_by_chat_id(chatID, whineNextMessage)


def whineNextMessage(msg):
    if not activeWhineMode:
        return
    text = msg.text
    if text == "/stop":
        stopMode(msg.chat.id)
        return
    if text == "/start":
        bot.send_message(msg.chat.id, "Select a mode", reply_markup=genStartMarkup())
        return
    if text == "/status":
        status(msg)
        return
    if text == "/chance":
        setChance(msg)
        return
    if random.randint(1, 10) > replyChance:
        bot.register_next_step_handler_by_chat_id(msg.chat.id, whineNextMessage)
        return
    if not isNavin(msg.from_user.id):
        bot.send_message(msg.chat.id, getRandom(WHINES))

    bot.register_next_step_handler_by_chat_id(msg.chat.id, whineNextMessage)


def flameMode(chatID):
    global activeFlameMode
    activeFlameMode = True
    bot.send_message(chatID, "Flame Mode Activated")
    bot.register_next_step_handler_by_chat_id(chatID, flameNextMessage)
    activeFlameMode = True
    return


def flameNextMessage(msg):
    print(msg)
    if not activeFlameMode:
        return
    if msg.content_type == "sticker":
        print("sticker")
        bot.register_next_step_handler_by_chat_id(msg.chat.id, flameNextMessage)
        return
    text = msg.text
    if text == "/stop":
        stopMode(msg.chat.id)
        return
    if text == "/start":
        bot.send_message(msg.chat.id, "Select a mode", reply_markup=genStartMarkup())
        return
    if text == "/status":
        status(msg)
        return
    if text == "/chance":
        setChance(msg)
        return

    print(msg.text)

    if isNavin(msg.from_user.id):
        if random.randint(1, 10) > replyChance:
            bot.register_next_step_handler_by_chat_id(msg.chat.id, flameNextMessage)
            return
        if re.match("^want *", text.lower()) or re.match("^wan *", text.lower()) or re.match(re.compile(r'[^.!?]+\?'), text.lower()):
            bot.send_sticker(msg.chat.id, NO_STICKER)
        else:
            bot.send_message(msg.chat.id, getRandom(FLAMES))

    bot.register_next_step_handler_by_chat_id(msg.chat.id, flameNextMessage)


@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "Select a mode", reply_markup=genStartMarkup())
    resumeMode(msg.chat.id)


def stopMode(chatID):
    global activeCancelMode
    global activeFlameMode
    global activeWhineMode
    global activeNavinMode
    if activeWhineMode:
        bot.send_message(chatID, "Whine Mode Stopped")
        activeWhineMode = False
        return
    if activeFlameMode:
        bot.send_message(chatID, "Flame Mode Stopped")
        activeFlameMode = False
        return
    if activeCancelMode:
        bot.send_message(chatID, "Cancel Mode Stopped")
        activeCancelMode = False
        return
    if activeNavinMode:
        bot.send_message(chatID, "Navin Simulation Mode Stopped")
        activeNavinMode = False
        return
    bot.send_message(chatID, "No Active Mode")


@bot.message_handler(commands=['startKick'])
def startKick(msg):
    if isNavin(msg.from_user.id):
        bot.send_sticker(msg.chat.id, NO_STICKER)
        return
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

    try:
        data = dict[str(msg.chat.id)]
    except KeyError:
        bot.send_message(msg.chat.id, "Vote not started here")
        return
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


def td_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ('year', 60 * 60 * 24 * 365),
        ('month', 60 * 60 * 24 * 30),
        ('day', 60 * 60 * 24),
        ('hour', 60 * 60),
        ('minute', 60),
        ('second', 1)
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)


@bot.message_handler(commands=["status"])
def status(msg):
    if haveMode() is None:
        mode = "None"
    else:
        mode = haveMode()
    uptime = datetime.datetime.now() - startTime
    bot.send_message(msg.chat.id,
                     f"""
                     Status: Running\n
Active Mode: {mode}\n
Message sent: {count}\n
Reply Chance: {replyChance}\n
Uptime: {td_format(uptime)}""")


@bot.message_handler(commands=["chance"])
def setChance(msg):
    bot.send_message(msg.chat.id, "Input Integer (0-10)")
    bot.register_next_step_handler_by_chat_id(msg.chat.id, setReplyChance)


def setReplyChance(msg):
    global replyChance
    try:
        newChance = int(msg.text)
        replyChance = newChance
        bot.send_message(msg.chat.id, f"Successfully changed to {newChance}")
        resumeMode(msg.chat.id)
    except ValueError:
        bot.send_message(msg.chat.id, "Must be integer from 0 to 10")
        bot.register_next_step_handler_by_chat_id(msg.chat.id, setReplyChance)
        resumeMode(msg.chat.id)


def resumeMode(chatID):
    if haveMode() is not None:
        bot.send_message(chatID, F"Resuming {haveMode()}")
        if activeFlameMode:
            bot.register_next_step_handler_by_chat_id(chatID, flameNextMessage)
        if activeWhineMode:
            bot.register_next_step_handler_by_chat_id(chatID, whineNextMessage)
        # if activeCancelMode:
        #     # bot.register_next_step_handler_by_chat_id(chatID, flameNextMessage)
        if activeNavinMode:
            bot.register_next_step_handler_by_chat_id(chatID, navinSimulateNextMessage)


bot.remove_webhook()
bot.infinity_polling()
