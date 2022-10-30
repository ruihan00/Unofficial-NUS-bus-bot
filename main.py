import json
import math
from telebot import TeleBot, types
import requests
import os
from requests.auth import HTTPBasicAuth
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
token = os.environ.get("BUS_BOT_KEY")
bot = TeleBot(token)
authKey = HTTPBasicAuth(os.environ.get("API_USERNAME"), os.environ.get("API_PW"))
url = os.environ.get("API_URL")
BUS_LOC = [{'caption': 'Oei Tiong Ham Building', 'name': 'OTH', 'LongName': 'Oei Tiong Ham Building', 'ShortName': 'OTH Bldg', 'latitude': 1.319333, 'longitude': 103.818262}, {'caption': 'Botanic Gardens MRT', 'name': 'BG-MRT', 'LongName': 'Botanic Gardens MRT', 'ShortName': 'BG MRT', 'latitude': 1.322586, 'longitude': 103.816135}, {'caption': 'College Green', 'name': 'CG', 'LongName': 'College Green', 'ShortName': 'College Gr', 'latitude': 1.323345, 'longitude': 103.816273}, {'caption': 'University Town', 'name': 'UTOWN', 'LongName': 'University Town', 'ShortName': 'UTown', 'latitude': 1.303623, 'longitude': 103.774388}, {'caption': 'Raffles Hall', 'name': 'RAFFLES', 'LongName': 'Raffles Hall', 'ShortName': 'Raffles Hall', 'latitude': 1.300963, 'longitude': 103.772705}, {'caption': 'Kent Vale', 'name': 'KV', 'LongName': 'Kent Vale', 'ShortName': 'Kent Vale', 'latitude': 1.301816, 'longitude': 103.769533}, {'caption': 'EA', 'name': 'EA', 'LongName': 'EA', 'ShortName': 'EA', 'latitude': 1.300534, 'longitude': 103.770171}, {'caption': 'SDE 3', 'name': 'SDE3', 'LongName': 'SDE 3', 'ShortName': 'SDE 3', 'latitude': 1.297756, 'longitude': 103.770043}, {'caption': 'Information Technology', 'name': 'IT', 'LongName': 'Information Technology', 'ShortName': 'IT', 'latitude': 1.297204, 'longitude': 103.772688}, {'caption': 'Opp Yusof Ishak House', 'name': 'YIH-OPP', 'LongName': 'Opp Yusof Ishak House', 'ShortName': 'Opp YIH', 'latitude': 1.298904, 'longitude': 103.774118}, {'caption': "Prince George's Park", 'name': 'PGP', 'LongName': "Prince George's Park", 'ShortName': 'PGP', 'latitude': 1.291765, 'longitude': 103.780419}, {'caption': 'Kent Ridge MRT', 'name': 'KR-MRT', 'LongName': 'Kent Ridge MRT', 'ShortName': 'KR MRT', 'latitude': 1.29483, 'longitude': 103.784439}, {'caption': 'LT 27', 'name': 'LT27', 'LongName': 'LT 27', 'ShortName': 'LT 27', 'latitude': 1.297421, 'longitude': 103.780941}, {'caption': 'University Hall', 'name': 'UHALL', 'LongName': 'University Hall', 'ShortName': 'UHall', 'latitude': 1.297372, 'longitude': 103.778075}, {'caption': 'Opp University Health Centre', 'name': 'UHC-OPP', 'LongName': 'Opp University Health Centre', 'ShortName': 'Opp UHC', 'latitude': 1.298786, 'longitude': 103.77563}, {'caption': 'Yusof Ishak House', 'name': 'YIH', 'LongName': 'Yusof Ishak House', 'ShortName': 'YIH', 'latitude': 1.298885, 'longitude': 103.774377}, {'caption': 'Central Library', 'name': 'CLB', 'LongName': 'Central Library', 'ShortName': 'CLB', 'latitude': 1.296544, 'longitude': 103.772569}, {'caption': 'Opp SDE 3', 'name': 'SDE3-OPP', 'LongName': 'Opp SDE 3', 'ShortName': 'Opp SDE 3', 'latitude': 1.297799, 'longitude': 103.769603}, {'caption': 'The Japanese Primary School', 'name': 'JP-SCH-16151', 'LongName': 'The Japanese Primary School', 'ShortName': 'Jpn Pr Sch', 'latitude': 1.30077, 'longitude': 103.769904}, {'caption': 'Museum', 'name': 'MUSEUM', 'LongName': 'Museum', 'ShortName': 'Museum', 'latitude': 1.301081, 'longitude': 103.77369}, {'caption': 'University Health Centre', 'name': 'UHC', 'LongName': 'University Health Centre', 'ShortName': 'UHC', 'latitude': 1.29891, 'longitude': 103.776103}, {'caption': 'Opp University Hall', 'name': 'UHALL-OPP', 'LongName': 'Opp University Hall', 'ShortName': 'Opp UHall', 'latitude': 1.297518, 'longitude': 103.77813}, {'caption': 'S 17', 'name': 'S17', 'LongName': 'S 17', 'ShortName': 'S 17', 'latitude': 1.29756, 'longitude': 103.780718}, {'caption': 'Opp Kent Ridge MRT', 'name': 'KR-MRT-OPP', 'LongName': 'Opp Kent Ridge MRT', 'ShortName': 'Opp KR MRT', 'latitude': 1.294923, 'longitude': 103.784603}, {'caption': "Prince George's Park Residences", 'name': 'PGPR', 'LongName': "Prince George's Park Residences", 'ShortName': 'PGPR', 'latitude': 1.290969, 'longitude': 103.78109}, {'caption': 'Opp HSSML', 'name': 'HSSML-OPP', 'LongName': 'Opp Hon Sui Sen Memorial Library', 'ShortName': 'Opp HSSML', 'latitude': 1.292798, 'longitude': 103.774978}, {'caption': 'Opp NUSS', 'name': 'NUSS-OPP', 'LongName': 'Opp NUSS', 'ShortName': 'Opp NUSS', 'latitude': 1.293208, 'longitude': 103.772618}, {'caption': 'COM 2', 'name': 'COM2', 'LongName': 'COM 2', 'ShortName': 'COM 2', 'latitude': 1.29483, 'longitude': 103.773687}, {'caption': 'Ventus', 'name': 'LT13-OPP', 'LongName': 'Ventus', 'ShortName': 'Ventus', 'latitude': 1.29534, 'longitude': 103.770617}, {'caption': 'LT 13', 'name': 'LT13', 'LongName': 'LT 13', 'ShortName': 'LT 13', 'latitude': 1.294552, 'longitude': 103.770635}, {'caption': 'AS 5', 'name': 'AS5', 'LongName': 'AS 5', 'ShortName': 'AS 5', 'latitude': 1.293619, 'longitude': 103.771475}, {'caption': 'BIZ 2', 'name': 'BIZ2', 'LongName': 'BIZ 2', 'ShortName': 'BIZ 2', 'latitude': 1.293223, 'longitude': 103.775068}, {'caption': 'Kent Ridge Bus Terminal', 'name': 'KRB', 'LongName': 'Kent Ridge Bus Terminal', 'ShortName': 'KR Bus Ter', 'latitude': 1.29453, 'longitude': 103.769924}, {'caption': 'TCOMS', 'name': 'TCOMS', 'LongName': 'TCOMS', 'ShortName': 'TCOMS', 'latitude': 1.293654, 'longitude': 103.776898}, {'caption': 'Opp TCOMS', 'name': 'TCOMS-OPP', 'LongName': 'Opp TCOMS', 'ShortName': 'Opp TCOMS', 'latitude': 1.293789, 'longitude': 103.776715}]
server = Flask(__name__)
BUS_STOP_NAMES = ['OTH', 'BG-MRT', 'CG',
                  'UTOWN', 'RAFFLES', 'KV',
                  'EA', 'SDE3', 'IT', 'YIH-OPP',
                  'PGP', 'KR-MRT', 'LT27',
                  'UHALL', 'UHC-OPP', 'YIH',
                  'CLB', 'SDE3-OPP', 'JP-SCH-16151',
                  'MUSEUM', 'UHC', 'UHALL-OPP',
                  'S17', 'KR-MRT-OPP', 'PGPR',
                  'HSSML-OPP', 'NUSS-OPP', 'COM2',
                  'LT13-OPP', 'LT13', 'AS5',
                  'BIZ2', 'KRB', 'TCOMS', 'TCOMS-OPP', "COM3"]

BUS_SERVICES = ['A1', 'A2', 'BTC', 'D1', 'D2', 'E', 'K', 'L']

BUS_STOP_NAMES_MARKUP = None
BUS_SERVICES_MARKUP = None


def makeBtn(name):
    return types.KeyboardButton(name)

def genRefreshMarkup(stop):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.one_time_keyboard = True
    markup.add(InlineKeyboardButton("Refresh", callback_data=stop))
    return markup

def makeMarkUp(list):
    markup = types.ReplyKeyboardMarkup()
    for i in range(0, len(list)):
        if (i % 3 == 0):
            if (i + 1 >= len(list)):
                markup.row(makeBtn(list[i]))
            elif (i + 2 >= len(list)):
                markup.row(makeBtn(list[i]),
                           makeBtn(list[i + 1]))
            else:
                markup.row(makeBtn(list[i]),
                           makeBtn(list[i + 1]),
                           makeBtn(list[i + 2]))
    return markup


BUS_STOP_NAMES_MARKUP = makeMarkUp(BUS_STOP_NAMES)
BUS_SERVICES_MARKUP = makeMarkUp(BUS_SERVICES)


# data = requests.get(url + "/ServiceDescription", auth=authKey).json()
# for item in data["ServiceDescriptionResult"]["ServiceDescription"]:
#     busServices.append(item["Route"])
# print(busServices)
# param = {"busstopname": "OTH"}
# data = requests.get(url + "/ShuttleService", params = param, auth=authKey).json()["ShuttleServiceResult"]
#
# print(data["caption"])
# for item in data["shuttles"]:
#
#     print(item["name"])
#     for eta in item["_etas"]:
#         print(eta["eta"])
#     print("=================")
@bot.message_handler(commands=["start", "help"])
def start(message):
    intro = """Hi! This is an unofficial NUS Bus Info bot \n
/help : Open Guide \n
/queryBusTiming : Open Bus Stop keyboard \n
/queryBusService : Open Bus Service keyboard \n
/getRouteMap : Open Bus Route Map \n
 Send a location and find the nearest Bus Stop!"""
    bot.send_message(message.chat.id, intro)


@bot.message_handler(commands=["stops"])
def queryBusTiming(message):
    bot.send_message(message.chat.id, "Which Bus Stop?", reply_markup=BUS_STOP_NAMES_MARKUP)


@bot.message_handler(commands=["services"])
def queryBusService(message):
    bot.send_message(message.chat.id, "Which Bus Service? ", reply_markup=BUS_SERVICES_MARKUP)


@bot.message_handler(commands=["map"])
def sendRouteMap(message):
    routeMap = open("Network-Map.jpeg", "rb")
    bot.send_photo(message.chat.id, routeMap)


@bot.message_handler(func=lambda message: message.text in BUS_STOP_NAMES, content_types=["text"])
def findTiming(message):
    param = {"busstopname": message.text}
    data = requests.get(url + "/ShuttleService", params=param, auth=authKey).json()["ShuttleServiceResult"]
    busStopName = data["caption"]
    str = busStopName

    for busService in data["shuttles"]:
        busServiceName = busService["name"]
        str += f"\n \n{busServiceName}: "
        if "PUB" in busServiceName:
            str += f"{busService['arrivalTime']}"
        else:
            serviceList = busService["_etas"]
            if (len(serviceList) == 0):
                str += "No Service"
            else:
                for i in range(0, len(serviceList)):
                    bus = busService["_etas"][i]
                    str += f"{bus['eta']}"
                    if (i < len(serviceList) - 1):
                        str += " | "

    msgid = bot.send_message(message.chat.id, str)
    bot.edit_message_reply_markup(message.chat.id, msgid, reply_markup=genRefreshMarkup(message.text))

@bot.callback_query_handler(func=lambda call: True)
def refreshMessgae(call):
    stopName = call.data
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    param = {"busstopname": stopName}
    data = requests.get(url + "/ShuttleService", params=param, auth=authKey).json()["ShuttleServiceResult"]
    busStopName = data["caption"]
    str = busStopName

    for busService in data["shuttles"]:
        busServiceName = busService["name"]
        str += f"\n \n{busServiceName}: "
        if "PUB" in busServiceName:
            str += f"{busService['arrivalTime']}"
        else:
            serviceList = busService["_etas"]
            if (len(serviceList) == 0):
                str += "No Service"
            else:
                for i in range(0, len(serviceList)):
                    bus = busService["_etas"][i]
                    str += f"{bus['eta']}"
                    if (i < len(serviceList) - 1):
                        str += " | "
    bot.edit_message_text(str, call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=genRefreshMarkup(stopName))


@bot.message_handler(func=lambda message: message.text in BUS_SERVICES, content_types=["text"])
def findRoute(message):
    param = {"route_code": message.text}
    data = requests.get(url + "/PickupPoint", params=param, auth=authKey).json()["PickupPointResult"]["pickuppoint"]
    str = f"{message.text} \n \n"
    for i in range(0, len(data)):
        stopName = data[i]["pickupname"]
        str += stopName
        if (i < len(data) - 1):
            str += "\n   ⇣   \n"

    bot.send_message(message.chat.id, str)



# @bot.message_handler(commands=["test"])
# def test(message):
#     data = requests.get(url + "/BusStops", auth = authKey).json()["BusStopsResult"]["busstops"]
#     print(data)

def computeDistance(lat1, long1, lat2, long2):
    radianConst = 180/math.pi
    radianLat1 = lat1 / radianConst
    radianLong1 = long1 / radianConst
    radianLat2 = lat2 / radianConst
    radianLong2 = long2 / radianConst
    earthRad = 3963.0
    mileToKiloConst = 1.609344
    return mileToKiloConst * earthRad * math.acos(math.sin(radianLat1) * math.sin(radianLat2)
                                                  + math.cos(radianLat1)
                                                  * math.cos(radianLat2)
                                                  * math.cos(radianLong2 - radianLong1))

@bot.message_handler(func=lambda message: True, content_types=["location"])
def findNearestBusStop(message):
    userLat = message.location.latitude
    userLong = message.location.longitude
    shortest_distance = math.inf
    nearestStop = None
    for stop in BUS_LOC:
        distance = computeDistance(userLat, userLong, stop["latitude"], stop["longitude"])
        if distance < shortest_distance:
            shortest_distance = distance
            nearestStop = stop
    msg = f"{nearestStop['LongName']} Stop ({nearestStop['name']}) is {math.trunc(shortest_distance * 1000)}m away!"
    bot.send_location(message.chat.id, latitude=nearestStop["latitude"], longitude=nearestStop["longitude"])
    bot.send_message(message.chat.id, msg)

@server.route('/' + token, methods = ["POST"])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url = "https://unofficial-nus-bus-bot.herokuapp.com/" + token)
    return "!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

# bot.infinity_polling()
