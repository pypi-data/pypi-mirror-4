# coding: utf-8

from controller import app
from player import play_it
import config


def serve():
    app.run(debug=True, use_reloader=False, port=config.port, host="")


def play():
    play_it()
