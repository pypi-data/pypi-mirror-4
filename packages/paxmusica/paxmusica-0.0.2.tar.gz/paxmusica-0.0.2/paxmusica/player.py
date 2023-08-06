#!/usr/bin/env python
from time import sleep
import model

def play_it():
    while True:
        model.play_and_update()
        sleep(0.2)


if __name__ == '__main__':
    play_it()
