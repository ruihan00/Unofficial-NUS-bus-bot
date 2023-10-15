import requests


try:
    requests.get(url='https://bus-bot.onrender.com/daily')

except Exception as e:
    print(e)

