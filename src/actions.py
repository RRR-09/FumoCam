# General use commands used frequently by other commands
import random
from winsound import Beep
from injector import *


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


def teleport(location_name, no_log=False):
    log_process("Teleport", no_log)
    print(f"'{location_name}'")
    if location_name == "":
        log(f"Please specify a location! Use one of the locations below:\n{', '.join(CFG.teleport_locations)}")
        sleep(5)
        log_process("")
        log("")
        return False
    if location_name not in CFG.teleport_locations:
        log(f"Unknown location! Please use one of the locations below:\n{', '.join(CFG.teleport_locations)}")
        sleep(5)
        log_process("")
        log("")
        return False
    elif CFG.next_possible_teleport > time.time() and not no_log:
        log(f"Teleport on cool-down! Please wait {round(CFG.next_possible_teleport - time.time())} seconds!")
        sleep(5)
        log_process("")
        log("")
        return False
    log(f"Teleporting to: {CFG.teleport_locations[location_name]['friendly_name']}", no_log)
    sleep(0.5)
    is_comedy = location_name == "comedy2"
    if not is_comedy:
        CFG.next_possible_teleport = time.time() + 30
    if not no_log:
        send_chat(f"[Teleporting to {CFG.teleport_locations[location_name]['friendly_name']}!]")
        sleep(5)
    Beep(40, 600)
    Beep(70, 400)
    chosen_location = CFG.teleport_locations[location_name]
    pos, rot, cam_rot = chosen_location["pos"], chosen_location["rot"], chosen_location["cam"]
    jump()
    inject_lua_file("teleport", pos=pos, rot=rot, cam_rot=cam_rot)
    if is_comedy:
        send_chat(random.choice(CFG.comedy_phrases))
    Beep(90, 300)
    sleep(1)
    if is_comedy:
        sleep(10)
        for i in range(5):
            log(f"Returning in {5 - i}s")
            Beep(90, 300)
            sleep(1)
        return_location = CFG.teleport_locations[CFG.current_location]
        pos, rot, cam_rot = return_location["pos"], return_location["rot"], return_location["cam"]
        inject_lua_file("teleport", pos=pos, rot=rot, cam_rot=cam_rot)
    else:
        CFG.current_location = location_name
    log("", no_log)
    log_process("", no_log)
    jump()  # If knocked over, clear sitting effect
    send_chat(CFG.current_emote)
    return True


def silent_teleport(location_name):
    chosen_location = CFG.teleport_locations[location_name]
    pos, rot, cam_rot = chosen_location["pos"], chosen_location["rot"], chosen_location["cam"]
    inject_lua_file("teleport", pos=pos, rot=rot, cam_rot=cam_rot)


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
    sleep(0.5)
    Beep(150, 100)
    button_x, button_y = round(SCREEN_RES["width"] * 0.5), round(SCREEN_RES["height"] * 0.95)  # Settings button
    pydirectinput.moveTo(button_x, button_y)
    alt_tab_click()
    Beep(100, 50)

    log("Toggling Collisions")
    sleep(0.5)
    Beep(150, 100)
    button_x, button_y = round(SCREEN_RES["width"] * 0.5), round(
        SCREEN_RES["height"] * 0.40)  # Toggle Collisions button
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
