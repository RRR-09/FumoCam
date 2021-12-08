from health import *  # Optimized import, contains all other src files down the line of dependency
from twitch_integration import *

async def queue_movement(action):  # todo: Simplify
    CFG.action_running = True
    log_process("Manual Movement")
    valid_keys = {"w": "Forward", "a": "Left", "s": "Backwards", "d": "Right"}
    key = action["move_key"].lower()
    if key not in valid_keys.keys():
        log(f"Not a valid movement! ({','.join(valid_keys)})")
        await async_sleep(5)
        log("")
        log_process("")
        CFG.action_running = False
        return False
    time_to_press = action["move_time"]
    log(f"Moving {valid_keys[key]} for {time_to_press} FC Units")
    await check_active()
    ACFG.move(direction_key=key, amount=time_to_press)
    log("")
    log_process("")
    CFG.action_running = False


async def queue_leap(action):  # todo: Simplify
    CFG.action_running = True
    log_process("Leap Forward")
    time_forward = action["forward_time"]
    time_jump = action["jump_time"]
    log(f"Moving forward for {time_forward}s and jumping for {time_jump}s")
    await check_active()
    ACFG.leap(forward_time=time_forward, jump_time=time_jump)
    log("")
    log_process("")
    CFG.action_running = False


async def do_process_queue():  # todo: Investigate benefits of multithreading over single-threaded/async
    if len(CFG.action_queue) == 0 or CFG.action_running:
        return
    CFG.action_running = True
    remove_duplicates = False
    while len(CFG.action_queue) > 0:
        print(CFG.action_queue)
        await check_active()
        await async_sleep(0.1)
        try:
            action = CFG.action_queue[0]
        except IndexError:
            log_process("ERROR")
            log("Error! You may have to re-input any commands\nyou requested from the bot.")
            sleep(5)
            log("")
            log_process("")
            return
        if action == "anti-afk":
            await do_anti_afk()
        elif action == "advert":
            await do_advert()
        elif "turn_camera_direction" in action:
            turn_direction = action['turn_camera_direction']
            turn_time = action['turn_camera_time']
            log_process(f"{turn_time} degrees {turn_direction.upper()}")            
            ACFG.look(direction=turn_direction, amount=turn_time)
            log_process("")
        elif "pitch_camera_direction" in action:
            pitch_direction = action['pitch_camera_direction']
            pitch_degrees = action['pitch_camera_degrees']
            log_process(f"Tilting {pitch_degrees} degrees {pitch_direction.upper()}")            
            ACFG.pitch(amount=pitch_degrees, up=pitch_direction == "up")
            log_process("")
        elif "zoom_camera_direction" in action:
            zoom_direction = "in" if action['zoom_camera_direction'] == "i" else "out"
            zoom_time = action['zoom_camera_time']
            log_process(f"Zooming {zoom_direction} {zoom_time}%")
            ACFG.zoom(zoom_direction_key=action['zoom_camera_direction'], amount=zoom_time)
            log_process("")
        elif "autonav" in action:
            location = action["autonav"]
            await auto_nav(location, slow_spawn_detect=False)
            log_process("")
            log("")
        elif action == "check_for_better_server":
            crashed = await do_crash_check()
            if not crashed:
                await check_for_better_server()
                await check_active()
            else:
                CFG.action_queue.insert(1, "handle_crash")
        elif "chat_with_name" in action:
            name = action["chat_with_name"][0]
            await send_chat(name)
            await async_sleep(len(name) * CFG.chat_name_sleep_factor)
            msgs = action["chat_with_name"][1:]
            for msg in msgs:
                await send_chat(msg)
        elif "chat" in action:
            for message in action["chat"]:
                await send_chat(message)
        elif action == "handle_crash":
            await handle_join_new_server(crash=True)
            remove_duplicates = True
        elif action == "handle_join_new_server":
            await handle_join_new_server()
            remove_duplicates = True
        elif action == "sit":
            await click_sit_button()
        elif action == "use":
            log_process("Pressing Use (e)")
            ACFG.use()
            log_process("")
            log("")
        elif action == "grief":
            await toggle_collisions()
            ACFG.resetMouse()
            log_process("")
            log("")
        elif action == "respawn":
            await respawn_character()
            log_process("")
            log("")
        elif action == "respawnforce":
            await force_respawn_character()
            log_process("")
            log("")
        elif action == "jump":
            ACFG.jump()
        elif "movement" in action:
            await queue_movement(action)
        elif "leap" in action:
            await queue_leap(action)
        elif "mute" in action:
            await mute_toggle(action["mute"])
        elif action == "rejoin":
            log_process("Rejoining!")
            kill_process(force=True)
            await async_sleep(5)
            log_process("")
            log("")
            await handle_join_new_server()
        elif "chat_move_mouse" in action:
            params = action["chat_move_mouse"]
            had_to_move, area = await move_mouse_chat_cmd(params["x"],params["y"])
            await async_sleep(2)
            if had_to_move:
                try:
                    await params["twitch_ctx"].send(f"[Can't move near '{area}'! Moved mouse to safe range nearby.]")
                except:
                    print(format_exc())
            log_process("")
            log("")
        elif action == "click":
            await chat_mouse_click()
            log_process("")
            log("")
        elif action == "backpack":
            await click_backpack_button()
            log_process("")
            log("")
        elif "item" in action:
            item_number = action["item"]
            await click_item(item_number)
            log_process("")
            log("")
        elif action == "hidemouse":
            ACFG.resetMouse()
            log_process("")
            log("")
        else:
            print("queue failed")
        CFG.action_queue.pop(0)
        if remove_duplicates:
            original_queue = CFG.action_queue
            for action_queue_item in original_queue:
                if isinstance(action_queue_item, dict) and list(action.keys())[-1] in action_queue_item:
                    CFG.action_queue.remove(action_queue_item)
                elif action == action_queue_item
                    CFG.action_queue.remove(action_queue_item)
    await async_sleep(0.1)
    CFG.action_running = False


async def add_action_queue(item):
    CFG.action_queue.append(item)
    await do_process_queue()


async def async_main():
    print("[Async_Main] Start")
    await CFG.add_action_queue({"mute": False})


def main():
    CFG.anti_afk = 0
    log_process("")
    log("")
    output_log("collisions", "")
    output_log("change_server_status_text", "")
    CFG.anti_afk_runs = 0
    CFG.add_action_queue = add_action_queue
    CFG.async_main = async_main
    twitch_main()


if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    main()