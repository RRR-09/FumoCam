# General use commands used frequently by other commands
import random
from winsound import Beep
from arduino_integration import *
from spawn_detection import spawn_detection_main
ACFG.initalize_serial_interface(do_log=False)


async def send_chat(message):
    await check_active()
    for word in CFG.censored_words:  # todo: More effective censoring
        if word in message:
            message = message.replace(word, "*" * len(word))
    ACFG.send_message(message)


async def do_anti_afk():
    await check_active()
    ACFG.look(direction="left", amount=45)
    await async_sleep(1)
    ACFG.look(direction="right", amount=90)
    await async_sleep(1)
    ACFG.look(direction="left", amount=45)


async def do_advert():
    for message in CFG.advertisement:
        await send_chat(message)


async def toggle_collisions():
    await check_active()
    await async_sleep(1)
    log("Opening Settings")
    Beep(150, 100)
    button_x, button_y = round(SCREEN_RES["width"] * 0.5), round(SCREEN_RES["height"] * 0.98)  # Settings button
    ACFG.moveMouseAbsolute(x=button_x, y=button_y)
    ACFG.left_click()

    log("Toggling Collisions")
    await async_sleep(0.25)
    Beep(150, 100)
    button_x, button_y = round(SCREEN_RES["width"] * 0.5), round(
        SCREEN_RES["height"] * 0.53)  # Toggle Collisions button
    ACFG.moveMouseAbsolute(x=button_x, y=button_y)
    ACFG.left_click()
    Beep(100, 50)
    CFG.collisions_disabled = not(CFG.collisions_disabled)
    collisions_msg = "" if CFG.collisions_disabled else "[WARN] Griefing/Collisions enabled!"
    output_log("collisions", collisions_msg)
    log("Closing Settings")
    await async_sleep(0.25)
    Beep(150, 100)
    button_x, button_y = round(SCREEN_RES["width"] * 0.5), round(
        SCREEN_RES["height"] * 0.30)  # Toggle Collisions button
    ACFG.moveMouseAbsolute(x=button_x, y=button_y)
    ACFG.left_click()
    await async_sleep(0.25)
    Beep(100, 50)
