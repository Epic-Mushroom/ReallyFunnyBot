from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
  return "we're so back"


def run():
  app.run(host='0.0.0.0', port=8080)

#function to keep the bot awake
def keep_awake():
  t = Thread(target=run)
  t.start()