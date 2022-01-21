import os
from asyncio import sleep as async_sleep
from shutil import copyfile
from subprocess import Popen  # nosec
from time import sleep
from typing import Tuple, Union

from pyautogui import position as get_mouse_position

from arduino_integration import ACFG, CFG
from config import OBS
from utilities import (
    check_active,
    kill_process,
    log,
    log_process,
    notify_admin,
    output_log,
)

ACFG.initalize_serial_interface(do_log=False)


async def send_chat(message: str, ocr=False):
    await check_active()
    for word in CFG.censored_words:  # TODO: More effective censoring
        if word in message:
            message = message.replace(word, "*" * len(word))
    if ocr:
        ACFG.send_message(message, ocr=True)
    else:
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
        await async_sleep(len(message) * CFG.chat_name_sleep_factor)


async def respawn_character(notify_chat: bool = True):
    await check_active()
    log_process("Respawning")
    if notify_chat:
        await send_chat("[Respawning!]")
    await async_sleep(0.75)
    ACFG.jump()
    await async_sleep(0.75)
    ACFG.keyPress("KEY_ESC")
    await async_sleep(0.5)
    ACFG.keyPress("r")
    await async_sleep(0.5)
    ACFG.keyPress("KEY_RETURN")
    await async_sleep(0.5)
    log_process("")


async def mute_toggle(set_mute: Union[bool, None] = None):
    log_process("In-game Mute")
    desired_mute_state = not CFG.audio_muted
    if set_mute is not None:  # If specified, force to state
        desired_mute_state = set_mute
    desired_volume = 0 if desired_mute_state else 100
    log_msg = "Muting" if desired_mute_state else "Un-muting"
    log(log_msg)
    sc_exe_path = str(CFG.resources_path / CFG.sound_control_executable_name)
    os.system(  # nosec
        f'{sc_exe_path} /SetVolume "{CFG.game_executable_name}" {desired_volume}'
    )

    # Kill the process no matter what, race condition for this is two songs playing (bad)
    kill_process(executable=CFG.vlc_executable_name, force=True)

    if desired_mute_state:  # Start playing music
        copyfile(
            CFG.resources_path / OBS.muted_icon_name,
            OBS.output_folder / OBS.muted_icon_name,
        )
        vlc_exe_path = str(CFG.vlc_path / CFG.vlc_executable_name)
        music_folder = str(CFG.resources_path / "soundtracks" / "overworld")
        Popen(
            f'"{vlc_exe_path}" --playlist-autostart --loop --playlist-tree {music_folder}'
        )
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


async def test_chat_mouse_pos(
    target_x: int, target_y: int
) -> Tuple[bool, str, int, int]:
    # Clamp to restrictions
    had_to_move, area = False, ""
    need_test = True
    while need_test:
        # Code is deliberatly very redundant for readability, logic is complex
        need_test = False
        for region in CFG.mouse_blocked_regions:
            target_right_of_region_left = target_x > region.x1
            target_left_of_region_right = target_x < region.x2
            target_in_between_region_widths = (
                target_right_of_region_left and target_left_of_region_right
            )
            if not (target_in_between_region_widths):
                continue

            target_below_region_top = target_y > region.y1
            target_above_region_bottom = target_y < region.y2
            target_in_between_region_heights = (
                target_below_region_top and target_above_region_bottom
            )
            if not (target_in_between_region_heights):
                continue

            need_test = True
            # Only offset the axis that is the smallest range of the region
            region_width = region.x2 - region.x1
            region_height = region.y2 - region.y1

            taller_than_wide = region_width < region_height
            if taller_than_wide:
                region_x_center = (region.x1 + region.x2) / 2
                right_of_region_center = target_x > region_x_center
                right_of_region_is_on_screen = (
                    region.x2 + CFG.mouse_blocked_safety_padding
                ) < CFG.screen_res["width"]

                if right_of_region_center and right_of_region_is_on_screen:
                    target_x = region.x2  # Target right of region
                else:
                    target_x = region.x1  # Target left of region
            else:
                region_y_center = (region.y1 + region.y2) / 2
                below_region_center = target_y > region_y_center
                region_bottom_is_on_screen = (
                    region.y2 + CFG.mouse_blocked_safety_padding
                ) < CFG.screen_res["height"]

                if below_region_center and region_bottom_is_on_screen:
                    target_y = region.y2  # Target bottom of region
                else:
                    target_y = region.y1  # Target top of region

            # If we have to move multiple times, only log the first reason
            if not had_to_move:
                had_to_move = True
                area = region.name
            break
    return had_to_move, area, target_x, target_y


async def move_mouse_chat_cmd(x: int, y: int):
    desired_x = CFG.screen_res["center_x"] + x
    desired_y = CFG.screen_res["center_y"] + y

    # Clamp
    target_x = min(CFG.screen_res["width"] - 1, desired_x)
    target_y = min(CFG.screen_res["height"] - 1, desired_y)
    target_x = max(1, target_x)
    target_y = max(1, target_y)

    had_to_move, area, target_x, target_y = await test_chat_mouse_pos(
        target_x, target_y
    )

    # Re-clamp
    target_x = min(CFG.screen_res["width"] - 1, target_x)
    target_y = min(CFG.screen_res["height"] - 1, target_y)
    target_x = max(1, target_x)
    target_y = max(1, target_y)

    print(target_x, target_y)
    ACFG.moveMouseAbsolute(x=target_x, y=target_y)
    ACFG.middle_click_software()
    return had_to_move, area


async def chat_mouse_click():
    log_process("Left Clicking")
    mouse_x, mouse_y = get_mouse_position()[0], get_mouse_position()[1]
    print("Got mouse position")
    had_to_move, area, _, __ = await test_chat_mouse_pos(mouse_x, mouse_y)
    if had_to_move:
        log(f"Mouse is in unsafe spot (near {area}), relocating...")
        await move_mouse_chat_cmd(mouse_x, mouse_y)
        sleep(2)
    ACFG.left_click()
