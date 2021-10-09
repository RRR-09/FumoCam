# General use commands used frequently by other commands
import random
from winsound import Beep
import threading
from utilities import *


def send_chat(message):
    check_active()
    pyautogui.press('/')
    sleep(0.1)
    for word in CFG.censored_words:  # todo: More effective censoring
        if word in message:
            message = message.replace(word, "*" * len(word))
    pyautogui.write(message)  # todo: investigate long messages only partially coming through
    sleep(0.5)
    pydirectinput.press('enter')


def turn_camera(direction_obj):
    direction = direction_obj["turn_camera_direction"]
    turn_time = direction_obj["turn_camera_time"]
    check_active()
    sleep(0.5)
    pydirectinput.keyDown(direction)
    sleep(turn_time)
    pydirectinput.keyUp(direction)
    sleep(1)


def jump():
    check_active()
    sleep(0.75)
    pydirectinput.keyDown('space')
    sleep(0.25)
    pydirectinput.keyUp('space')


def do_anti_afk():
    check_active()
    sleep(0.5)
    pydirectinput.keyDown('left')
    sleep(0.75)
    pydirectinput.keyUp('left')
    sleep(1)
    pydirectinput.keyDown('right')
    sleep(1.5)
    pydirectinput.keyUp('right')
    sleep(1)
    pydirectinput.keyDown('left')
    sleep(0.65)
    pydirectinput.keyUp('left')


def do_advert():
    print("DoAdvert")
    for message in CFG.advertisement:
        send_chat(message)


def toggle_collisions():
    check_active()
    log("Opening Settings")
    sleep(1)
    Beep(150, 100)
    button_x, button_y = round(SCREEN_RES["width"] * 0.5), round(SCREEN_RES["height"] * 0.95)  # Settings button
    pydirectinput.moveTo(button_x, button_y)
    alt_tab_click()
    Beep(100, 50)

    log("Toggling Collisions")
    sleep(0.5)
    Beep(150, 100)
    button_x, button_y = round(SCREEN_RES["width"] * 0.5), round(
        SCREEN_RES["height"] * 0.50)  # Toggle Collisions button
    pydirectinput.moveTo(button_x, button_y)
    alt_tab_click()
    Beep(100, 50)

    log("Closing Settings")
    sleep(0.25)
    Beep(150, 100)
    button_x, button_y = round(SCREEN_RES["width"] * 0.5), round(
        SCREEN_RES["height"] * 0.30)  # Toggle Collisions button
    pydirectinput.moveTo(button_x, button_y)
    alt_tab_click()
    sleep(0.25)
    Beep(100, 50)
