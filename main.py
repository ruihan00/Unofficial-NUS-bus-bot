from flask import Flask, request
from affirmation_bot.affirmation_bot import affirmations_bot_route, dailyJob
from busbot.main import bus_bot_route
from kickbot.kickBot import kickbot_route
from tech_bar_bot.tech_bar_bot import tech_bar_route, URL_PREFIX, dailyReminder
import os

server = Flask(__name__)

schedule_key = os.environ.get('SCHEDULE_KEY')
@server.route('/' , methods = ["GET"])
def getMessage():
    return "Rui Han's bot farm", 200

@server.route('/daily' + schedule_key, methods = ['GET'])
def dailyRunner():
    dailyJob()
    dailyReminder()
    return 'Success', 200

server.register_blueprint(affirmations_bot_route, url_prefix='/affirmationsBot')
server.register_blueprint(bus_bot_route, url_prefix='/busBot')
server.register_blueprint(kickbot_route, url_prefix='/kickBot')
server.register_blueprint(tech_bar_route, url_prefix=f"/{URL_PREFIX}")

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))