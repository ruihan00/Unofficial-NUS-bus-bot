from flask import Flask, request
from affirmation_bot.affirmation_bot import affirmations_bot_route, dailyJob
from busbot.main import bus_bot_route
from kickbot.kickBot import kickbot_route
import os

server = Flask(__name__)
@server.route('/' , methods = ["GET"])
def getMessage():
    return "Rui Han's bot farm", 200

@server.route('/daily', methods = ['GET'])
def dailyRunner():
    dailyJob()

server.register_blueprint(affirmations_bot_route, url_prefix='/affirmationsBot')
server.register_blueprint(bus_bot_route, url_prefix='/busBot')
server.register_blueprint(kickbot_route, url_prefix='/kickBot')
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))