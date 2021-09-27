from health import *  # Optimized import, contains all other src files down the line of dependency
from twitch_integration import *


def rel_coord(x, y):
    return round(x * SCREEN_RES["x_multi"]), round(y * SCREEN_RES["y_multi"])


def loop_anti_afk():
    seconds_in_minute = 60
    afk_minutes = 10
    delay_duration = seconds_in_minute * afk_minutes
    while True:
        sleep(delay_duration)
        CFG.action_queue.append("anti-afk")
        sleep(delay_duration)
        CFG.action_queue.append("anti-afk")
        sleep(delay_duration)
        CFG.action_queue.append("anti-afk")
        CFG.action_queue.append("advert")


def loop_check_better_server():
    while True:
        CFG.action_queue.append("check_for_better_server")
        sleep(5 * 60)


def loop_clock():
    while True:
        output_log("clock", time.strftime("%Y-%m-%d \n%I:%M:%S%p EST"))
        sleep(1)


def loop_crash_check():
    while True:
        crashed = do_crash_check()
        if crashed:
            CFG.action_queue.append("handle_crash")
            sleep(60)
        sleep(5)


def loop_help():
    commands_list = [
        {
            "command": "!m Your Message",
            "help": "Sends \"Your Message\" in-game"
        },
        {
            "help": f"Teleport. \n({', '.join(CFG.teleport_locations)})",
            "command": "!tp LocationName",
            "injector_status_required": True,
            "time": 20
        },
        {
            "command": "!goto PlayerName",
            "help": "Teleports to a player by that name.",
            "injector_status_required": True
        },
        {
            "command": "!spectate",
            "help": "Spectates up to 10 random players.",
            "injector_status_required": True
        },
        {
            "command": "!tour",
            "help": "Goes on a tour to all known locations.",
            "injector_status_required": True
        },
        {
            "command": "!left 0.2 or !right 0.2",
            "help": "Turn camera left or right for 0.2s"
        },
        {
            "command": "!zoomin 0.1 or !zoomout 0.1",
            "help": "Zoom camera in or out for 0.1s"
        },
        {
            "command": "!sit",
            "help": "Clicks the sit button"
        },
        {
            "command": "!dev Your Message",
            "help": "EMERGENCY ONLY, Sends \"Your Message\" to devs discord account"
        },
        {
            "command": "!move w 5",
            "help": "Moves forwards for 5 seconds",
            "injector_status_required": False
        },
        {
            "command": "!leap 0.7 0.5",
            "help": "At the same time, moves forwards for 0.7s and jumps for 0.5s",
            "injector_status_required": False
        },
        {
            "command": "!jump",
            "help": "Jumps. Helpful if stuck on something.",
            "injector_status_required": False
        },
        {
            "command": "!grief",
            "help": "Toggles anti-grief.",
            "injector_status_required": False
        },
        {
            "command": "!respawn",
            "help": "Respawns. Helpful if completely stuck.",
            "injector_status_required": False
        },
        {
            "command": "!use",
            "help": "Presses \"e\".",
            "injector_status_required": False
        },
        {
            "command": "!sit",
            "help": "Clicks the sit button.",
            "injector_status_required": False
        },
    ]
    while True:
        new_commands_list = []
        for cmd in commands_list:
            if "injector_status_required" in cmd:
                # If the injector needs to be ON for this but its OFF
                if cmd["injector_status_required"] and CFG.injector_disabled:
                    continue
                # If the injector needs to be OFF for this but its ON
                if not cmd["injector_status_required"] and not CFG.injector_disabled:
                    continue
            new_commands_list.append(cmd)
        for command in new_commands_list:
            output_log("commands_help_label", "")
            output_log("commands_help_title", "")
            output_log("commands_help_desc", "")

            sleep(0.25)
            current_command_in_list = f"{(new_commands_list.index(command) + 1)}/{len(new_commands_list)}"
            output_log("commands_help_label", f"TWITCH CHAT COMMANDS [{current_command_in_list}]")
            output_log("commands_help_title", command["command"])
            sleep(0.1)
            output_log("commands_help_desc", command["help"])
            if "time" in command:
                sleep(int(command["time"]))
                continue
            sleep(5)


def loop_spectate():
    while True:
        sleep(15 * 60)
        if CFG.injector_disabled:
            continue
        CFG.next_possible_teleport = 0
        CFG.action_queue.append("spectate")


def loop_timer():
    event_time_struct = time.strptime(OBS.event_time, "%Y-%m-%d %I:%M:%S%p")
    # event_end_time_struct = time.strptime(OBS.event_end_time, "%Y-%m-%d %I:%M:%S%p")
    while CFG.event_timer_running:
        seconds_since_event = time.time() - time.mktime(event_time_struct)
        english_time_since_event = get_english_timestamp(seconds_since_event)
        output_log("time_since_event", english_time_since_event)
        sleep(1)


def queue_movement(action):  # todo: Simplify
    CFG.action_running = True
    log_process("Manual Movement")
    if not CFG.injector_disabled and not action["override"]:
        log("Manual movement not allowed when injector is working!")
        sleep(5)
        log_process("")
        log("")
    valid_keys = {"w": "Forward", "a": "Left", "s": "Backwards", "d": "Right"}
    key = action["move_key"].lower()
    if key not in valid_keys.keys():
        log(f"Not a valid movement! ({','.join(valid_keys)})")
        sleep(5)
        log("")
        log_process("")
        CFG.action_running = False
        return False
    time_to_press = action["move_time"]
    log(f"Moving {valid_keys[key]} for {time_to_press}s")
    check_active()
    sleep(0.75)
    pydirectinput.keyDown(key)
    sleep(time_to_press)
    pydirectinput.keyUp(key)
    log("")
    log_process("")
    CFG.action_running = False


def queue_leap(action):  # todo: Simplify
    CFG.action_running = True
    log_process("Leap Forward")
    if not CFG.injector_disabled and not action["override"]:
        log("Manual movement not allowed when injector is working!")
        sleep(5)
        log_process("")
        log("")
    time_forward = action["forward_time"]
    time_jump = action["jump_time"]
    log(f"Moving forward for {time_forward}s and jumping for {time_jump}s")
    check_active()
    sleep(0.75)
    pydirectinput.keyDown("w")
    pydirectinput.keyDown("space")
    if time_forward > time_jump:
        sleep(time_jump)
        pydirectinput.keyUp("space")
        sleep(time_forward - time_jump)
        pydirectinput.keyUp("w")
    else:
        sleep(time_forward)
        pydirectinput.keyUp("w")
        sleep(time_jump - time_forward)
        pydirectinput.keyUp("space")
    log("")
    log_process("")
    CFG.action_running = False


def do_process_queue():  # todo: Investigate benefits of multithreading over single-threaded/async
    if len(CFG.action_queue) > 0:
        action = CFG.action_queue[0]
        print(CFG.action_queue)
        if action == "anti-afk":
            CFG.action_running = True
            do_anti_afk()
            CFG.action_running = False
        elif action == "advert":
            CFG.action_running = True
            do_advert()
            CFG.action_running = False
        elif "turn_camera_direction" in action:
            CFG.action_running = True
            turn_direction = action['turn_camera_direction']
            turn_time = action['turn_camera_time']
            log_process(f"{turn_direction.upper()} for {turn_time}s")
            turn_camera(action)
            log_process("")
            CFG.action_running = False
        elif "zoom_camera_direction" in action:
            CFG.action_running = True
            zoom_direction = "in" if action['zoom_camera_direction'] == "i" else "out"
            zoom_time = action['zoom_camera_time']
            log_process(f"Zooming {zoom_direction} for {zoom_time}s")
            zoom_camera(action)
            log_process("")
            CFG.action_running = False
        elif action == "check_for_better_server":
            crashed = do_crash_check()
            if not crashed:
                check_for_better_server()
                check_active()
            else:
                CFG.action_queue.insert(0, "handle_crash")
        elif "chat_with_name" in action:
            name = action["chat_with_name"][0]
            send_chat(name)
            sleep(len(name) * CFG.chat_name_sleep_factor)
            msgs = action["chat_with_name"][1:]
            for msg in msgs:
                send_chat(msg)
        elif "chat" in action:
            for message in action["chat"]:
                send_chat(message)
        elif action == "handle_crash":
            CFG.action_running = True
            handle_join_new_server(crash=True)
            CFG.action_running = False
        elif action == "handle_join_new_server":
            CFG.action_running = True
            handle_join_new_server()
            CFG.action_running = False
        elif "tp" in action:
            CFG.action_running = True
            teleport(action["tp"])
            check_active()
            CFG.action_running = False
        elif "goto" in action:
            CFG.action_running = True
            goto(action["goto"])
            check_active()
            CFG.action_running = False
        elif action == "spectate":
            CFG.action_running = True
            spectate_random()
            check_active()
            CFG.action_running = False
        elif action == "tour":
            CFG.action_running = True
            world_tour()
            check_active()
            CFG.action_running = False
        elif action == "click":
            CFG.action_running = True
            alt_tab_click()
            CFG.action_running = False
        elif action == "sit":
            CFG.action_running = True
            click_sit_button()
            CFG.action_running = False
        elif action == "use":
            CFG.action_running = True
            log_process("Pressing Use (e)")
            if not CFG.injector_disabled:
                log("Manual control not allowed when injector is working!")
                sleep(5)
            else:
                check_active()
                pydirectinput.keyDown("e")
                sleep(1)
                pydirectinput.keyUp("e")
            log_process("")
            log("")
            CFG.action_running = False
        elif action == "grief":
            CFG.action_running = True
            if not CFG.injector_disabled:
                log("Anti-Grief toggling not allowed when injector is working!")
                sleep(5)
            else:
                toggle_collisions()
                pydirectinput.moveTo(1, 1)
                alt_tab_click()
            log_process("")
            log("")
            CFG.action_running = False
        elif action == "respawn":
            CFG.action_running = True
            if not CFG.injector_disabled:
                log("Respawning character not allowed when injector is working!")
                sleep(5)
            else:
                respawn_character()
            log_process("")
            log("")
            CFG.action_running = False
        elif action == "jump":
            CFG.action_running = True
            jump()
            CFG.action_running = False
        elif "movement" in action:
            queue_movement(action)
        elif "leap" in action:
            queue_leap(action)
        else:
            print("queue failed")
        CFG.action_queue.pop(0)


def loop_process_queue():
    while True:
        sleep(CFG.tick_rate_blocked)
        if CFG.action_running:
            continue
        do_process_queue()
        sleep(CFG.tick_rate)


def main():
    log_process("")
    log("")
    output_log("change_server_status_text", "")
    output_log("injector_failure", "")
    crashed = do_crash_check()
    if crashed or "Roblox" not in pyautogui.getAllTitles():
        CFG.action_queue.append("handle_crash")
        do_process_queue()
    else:
        check_active()
        load_exploit()
    print("Starting Threads")
    thread_functions = [loop_process_queue, loop_check_better_server, twitch_main, loop_anti_afk, loop_help, loop_timer,
                        loop_clock, loop_crash_check, loop_spectate]
    for thread_function in thread_functions:
        threading.Thread(target=thread_function).start()
    print("Done Main")


if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    main()
