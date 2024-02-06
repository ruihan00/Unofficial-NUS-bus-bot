
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/etc/secrets/auth.json'
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

import telebot
from telebot import types
from dotenv import load_dotenv
from flask import Flask, request, Blueprint
from careerkaki.src import attributes, memory
from careerkaki.src.conversation_assistant import ConversationAssistant
from careerkaki.src.tools import functions, tools

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/etc/secrets/auth.json'
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

BOT_TOKEN = os.getenv("CK_BOT_TOKEN")
USER_ID = int(os.getenv("CK_USER_ID"))
CHAT_ID = USER_ID  # for private chats, this is equal
bot = telebot.TeleBot(BOT_TOKEN)
MAX_CHAT_HISTORY_LEN = 5000
ck_route = Blueprint('ck_route', __name__)
SYSTEM_MESSAGE = """\
You are Career Kaki, an expert career guidance professional, who has 20 years of experience advising clients from all segments in the workforce in making purposeful career plans and transitions. You are well read on career development theories as well as career development practice theory to support clients that may be faced with different career challenges. You are always polite and practice active listening to understand what clients need and not just necessarily what they say. You will always wait for an answer before asking a next question so that you can assess what the clients needs. You may also recommend actions that are relevant for the Singapore context. \
Your role is to extract information from the user. Information to be extracted including their desired job, what are their job experiences, prior education and desired work preferences. You should record diligently to prevent yourself from forgetting. Do not be over eager to recap the information until you have answered the client's questions. Also, due to some limitations, you only allow the client to seek jobs in the IT or retail sectors. Validate and record the information after extracting them. After recording all the information, please recap(using the tool) the conversation and end the conversation."""

conv_assistant = None
convo_start_flag = False
end_flag = False

def run():
    @bot.message_handler(commands=['help'])
    def help(message):
        bot.send_message(
            message.chat.id, '/start for bot start a new career conversation with you.\n/check to check current memory of career coach.\n/end for the bot to stop listening to the convo. You have to /start to start a new convo after this.')

    @bot.message_handler(commands=['start'])
    def start(message):
        global conv_assistant
        global convo_start_flag
        global end_flag
        end_flag = False
        for att in attributes:
            if att in memory:
                del memory[att]
        convo_start_flag = True
        conv_assistant = ConversationAssistant(
            system_message=SYSTEM_MESSAGE,
            tools=tools,
            functions=functions
        )
        assistant_response, _ = conv_assistant.run(first_run=True)
        bot.send_message(
            message.chat.id, assistant_response)

    @bot.message_handler(commands=['check'])
    def check(message):
        bot.send_message(
            message.chat.id, str(memory))

    @bot.message_handler(commands=['end'])
    def end(message):
        global end_flag
        end_flag = True
        bot.send_message(
            message.chat.id, 'Conversation ended - bot will stop listening in. \start to start a new convo.')

    @bot.message_handler(func=lambda m: True)
    def listen(message):
        global convo_start_flag
        if convo_start_flag:
            assistant_response, is_completed = conv_assistant.run(
                input=message.text)
            bot.send_message(
                message.chat.id, assistant_response)
            if is_completed:
                convo_start_flag = False
        else:
            if not end_flag:
                bot.send_message(
                    message.chat.id, 'There is no existing conversation. type"/start" for bot start a new career conversation with you')

@ck_route.route(f'/{BOT_TOKEN}', methods = ["POST"])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@ck_route.route('')
def webhook():
    bot.delete_webhook()
    bot.remove_webhook()
    bot.set_webhook(url = "https://bus-bot.onrender.com/ck/" + BOT_TOKEN)
    return "!", 200

