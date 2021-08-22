from actions import *
from health import change_characters


def click_sit_button():
    log_process("Clicking Sit button")
    check_active()
    sleep(0.5)
    Beep(150, 100)
    try:
        ratio_x, ratio_y = CFG.sit_button_position
        x = round(SCREEN_RES["width"] * ratio_x)
        y = round(SCREEN_RES["height"] * ratio_y)
        pydirectinput.moveTo(x, y)
        alt_tab_click()
        Beep(100, 50)
    except Exception:
        log("Could not find sit button on screen?")
        sleep(5)
    log_process("")


def spectate_random():
    if CFG.injector_disabled:
        log(f"Cannot spectate, injector functionality is currently broken!")
        return False
    if CFG.next_possible_teleport > time.time():
        log(f"Spectate on cool-down! Please wait {round(CFG.next_possible_teleport - time.time())} seconds!")
        sleep(5)
        log_process("")
        log("")
        return False
    CFG.next_possible_teleport = time.time() + 30
    log_process("Spectating")
    log("Spectating up to 10 random players")
    send_chat("[Spectating players! Won't be able to see nearby chat. Be right back!]")

    inject_lua_file("spectate")
    sleep(10 * 5)  # todo: make configurable time, configurable amount of players, dynamic skip current player
    send_chat("[I'm back! Should be finished spectating players.]")
    log_process("")
    log("")


def respawn_character():
    check_active()
    log_process("Respawning")
    send_chat("[Respawning!]")
    change_characters(respawn=True)
    log_process("")


def goto(target):
    log_process("Goto")
    print(f"'{target}'")
    if target == "":
        log(f"Please specify a player!")
        sleep(5)
        log_process("")
        log("")
        return False
    if CFG.next_possible_teleport > time.time():
        log(f"Teleport on cool-down! Please wait {round(CFG.next_possible_teleport - time.time())} seconds!")
        sleep(5)
        log_process("")
        log("")
        return False
    log(f"Attempting teleport to player...\n(If this doesnt work, the name was incorrect)")
    sleep(0.5)
    CFG.next_possible_teleport = time.time() + 30
    Beep(40, 600)
    Beep(70, 400)
    # todo: Probably best to write LUA in separate files
    # noinspection LongLine
    jump()
    inject_lua_file("goto_player", target=target.lower())

    sleep(10)  # Initial Teleport
    Beep(90, 300)
    sleep(3)  # Skybox check
    jump()  # If knocked over, clear sitting effect
    send_chat(CFG.current_emote)
    log("")
    log_process("")
    return True


def world_tour():
    interval = CFG.seconds_per_tour_location
    locations = CFG.teleport_locations
    send_chat(f"[Going on tour. Try and keep up! I'll be back here in {len(locations) * interval} seconds.]")
    log_process("World Tour")
    sleep(5)
    locations_list = list(locations.keys())
    for index in range(len(locations_list)):
        if CFG.injector_disabled:
            break
        location_key = locations_list[index]
        location = locations[location_key]
        log(f"Touring {location['friendly_name']} ({index + 1}/{len(locations_list)})")
        CFG.next_possible_teleport = 0
        jump()
        silent_teleport(location_key)
        sleep(interval)

    if CFG.injector_disabled:
        crashed = do_crash_check()
        if crashed or "Roblox" not in pyautogui.getAllTitles():
            CFG.action_queue.append("handle_crash")
    CFG.next_possible_teleport = 0
    teleport(CFG.current_location, no_log=True)
    CFG.next_possible_teleport = time.time() + 30
    log("")
    log_process("")
    send_chat(f"[I'm back from my tour!]")


def zoom_camera(zoom_obj):
    zoom_direction = zoom_obj["zoom_camera_direction"]
    zoom_time = zoom_obj["zoom_camera_time"]
    check_active()
    sleep(0.5)
    pydirectinput.keyDown(zoom_direction)
    sleep(zoom_time)
    pydirectinput.keyUp(zoom_direction)
    sleep(0.5)
