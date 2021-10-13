# General use commands used frequently by other commands
import random
from winsound import Beep
from utilities import *


async def send_chat(message):
    await check_active()
    pyautogui.press('/')
    await async_sleep(0.1)
    for word in CFG.censored_words:  # todo: More effective censoring
        if word in message:
            message = message.replace(word, "*" * len(word))
    pyautogui.write(message)  # todo: investigate long messages only partially coming through
    await async_sleep(0.25)
    pydirectinput.press('enter')
    await async_sleep(0.5)


async def turn_camera(direction_obj):
    print("turning camera")
    direction = direction_obj["turn_camera_direction"]
    turn_time = direction_obj["turn_camera_time"]
    await check_active()
    pydirectinput.keyDown(direction)
    await async_sleep(turn_time)
    pydirectinput.keyUp(direction)
    await async_sleep(1)


async def jump():
    await check_active()
    pydirectinput.keyDown('space')
    await async_sleep(0.25)
    pydirectinput.keyUp('space')


async def do_anti_afk():
    await check_active()
    pydirectinput.keyDown('left')
    await async_sleep(0.75)
    pydirectinput.keyUp('left')
    await async_sleep(1)
    pydirectinput.keyDown('right')
    await async_sleep(1.5)
    pydirectinput.keyUp('right')
    await async_sleep(1)
    pydirectinput.keyDown('left')
    await async_sleep(0.65)
    pydirectinput.keyUp('left')


async def do_advert():
    for message in CFG.advertisement:
        await send_chat(message)


async def toggle_collisions():
    await check_active()
    await async_sleep(0.5)
    log("Opening Settings")
    Beep(150, 100)
    button_x, button_y = round(SCREEN_RES["width"] * 0.5), round(SCREEN_RES["height"] * 0.95)  # Settings button
    pydirectinput.moveTo(button_x, button_y)
    await alt_tab_click()
    Beep(100, 50)

    log("Toggling Collisions")
    await async_sleep(0.25)
    Beep(150, 100)
    button_x, button_y = round(SCREEN_RES["width"] * 0.5), round(
        SCREEN_RES["height"] * 0.50)  # Toggle Collisions button
    pydirectinput.moveTo(button_x, button_y)
    await alt_tab_click()
    Beep(100, 50)

    log("Closing Settings")
    await async_sleep(0.25)
    Beep(150, 100)
    button_x, button_y = round(SCREEN_RES["width"] * 0.5), round(
        SCREEN_RES["height"] * 0.30)  # Toggle Collisions button
    pydirectinput.moveTo(button_x, button_y)
    await alt_tab_click()
    await async_sleep(0.25)
    Beep(100, 50)
