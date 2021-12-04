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


async def respawn_character(chat=True):
    await check_active()
    log_process("Respawning")
    if chat:
        await send_chat("[Respawning!]")
    await async_sleep(0.75)
    ACFG.keyPress('KEY_ESC')
    await async_sleep(0.5)
    ACFG.keyPress('r')
    await async_sleep(0.5)
    ACFG.keyPress('KEY_RETURN')
    await async_sleep(0.5)
    log_process("")


async def mute_toggle(mute=None):
    log_process("In-game Mute")
    desired_mute_state = not CFG.audio_muted
    if mute is not None:  # If specified, force to state
        desired_mute_state = mute
    desired_volume = 0 if desired_mute_state else 100
    log_msg = "Muting" if desired_mute_state else "Un-muting"
    log(log_msg)
    os.system(f"{str(RESOURCES_PATH / CFG.sound_control_executable_name)} /SetVolume \"{CFG.game_executable_name}\" {desired_volume}")
    
    # Kill the process no matter what, race condition for this is two songs playing (bad)
    kill_process(executable=CFG.vlc_executable_name, force=True)
    
    if desired_mute_state:  # Start playing music
        copyfile(RESOURCES_PATH / OBS.muted_icon_name, OBS.output_folder / OBS.muted_icon_name)
        subprocess.Popen(f'"{str(CFG.vlc_path / CFG.vlc_executable_name)}" --playlist-autostart --loop --playlist-tree {str(RESOURCES_PATH / "soundtracks" / "overworld")}')
        output_log("muted_status", "In-game audio muted!\nRun !mute to unmute")
        sleep(5)  # Give it time to load VLC
    else:  # Stop playing music
        try:
            if os.path.exists(OBS.output_folder / OBS.muted_icon_name):
                os.remove(OBS.output_folder / OBS.muted_icon_name)
        except OSError:
            log("Error, could not remove icon!\nNotifying admin...")
            async_sleep(2)
            notify_admin("Mute icon could not be removed")
            log(log_msg)
        output_log("muted_status", "")
    CFG.audio_muted = desired_mute_state
    
    await check_active()
    log_process("")
    log("")


async def test_chat_mouse_pos(target_x, target_y):
    #Clamp to restrictions
    had_to_move, area = False, ""
    need_test = True
    while need_test:
        need_test = False
        #{"name": "Test", "x1": 0, "y1": 0, "x2":340, "y2":240}
        for region in CFG.mouse_blocked_regions:
            if target_x > region["x1"] and target_x < region["x2"]:
                if target_y > region["y1"] and target_y < region["y2"]:
                    need_test = True
                    #Only offset the axis that is the smallest range of the region
                    region_width = region["x2"] - region["x1"]
                    region_height = region["y2"] - region["y1"]
                    
                    if region_width < region_height:                    
                        region_x_center = (region["x1"]+region["x2"])/2
                        if target_x > region_x_center and region["x2"]+10 < SCREEN_RES["width"]:
                            target_x = region["x2"]
                        else:
                            target_x = region["x1"]
                    else:
                        region_y_center = (region["y1"]+region["y2"])/2
                        if target_y > region_y_center and region["y2"]+10 < SCREEN_RES["height"]:
                            target_y = region["y2"]
                        else:
                            target_y = region["y1"]
                    
                    if not had_to_move:  # If we have to move multiple times, only log the first reason
                        had_to_move = True
                        area = region["name"]
                    break
    return had_to_move, area, target_x, target_y


async def move_mouse_chat_cmd(x, y):
    desired_x = SCREEN_RES["center_x"] + x
    desired_y = SCREEN_RES["center_y"] + y
    
    #Clamp
    target_x = min(SCREEN_RES["width"]-1, desired_x)
    target_y = min(SCREEN_RES["height"]-1, desired_y)
    target_x = max(1, target_x)
    target_y = max(1, target_y)
    
    had_to_move, area, target_x, target_y = await test_chat_mouse_pos(target_x, target_y)
    
    #Re-clamp
    target_x = min(SCREEN_RES["width"]-1, target_x)
    target_y = min(SCREEN_RES["height"]-1, target_y)
    target_x = max(1, target_x)
    target_y = max(1, target_y)
    
    print(target_x, target_y)
    ACFG.moveMouseAbsolute(x=target_x, y=target_y)
    ACFG.middle_click_software()
    return had_to_move, area


async def chat_mouse_click():
    log_process("Left Clicking")
    mouse_x, mouse_y = get_mouse_position()[0], get_mouse_position()[1]
    had_to_move, area, target_x, target_y = await test_chat_mouse_pos(mouse_x, mouse_y)
    if had_to_move:
        log(f"Mouse is in unsafe spot (near {area}), relocating...")
        await move_mouse_chat_cmd(mouse_x, mouse_y)
        sleep(2)
    ACFG.left_click()