from asyncio import sleep as async_sleep
from json import loads as json_loads
from subprocess import check_output  # nosec
from time import sleep, time
from traceback import format_exc

import pyautogui
from lxml.html import document_fromstring  # nosec
from requests import get

from actions import (
    chat_mouse_click,
    do_advert,
    do_anti_afk,
    move_mouse_chat_cmd,
    mute_toggle,
    respawn_character,
    send_chat,
)
from chat_ocr import activate_ocr, deactivate_ocr
from commands import click_backpack_button, click_item, click_sit_button
from config import ActionQueueItem
from health import (
    ACFG,
    auto_nav,
    check_for_better_server,
    force_respawn_character,
    handle_join_new_server,
    toggle_collisions,
)
from twitch_integration import CFG, twitch_main
from utilities import (
    check_active,
    do_crash_check,
    kill_process,
    log,
    log_process,
    output_log,
)


async def do_process_queue():  # TODO: Investigate benefits of multithreading over single-threaded/async
    if len(CFG.action_queue) == 0 or CFG.action_running:
        return
    CFG.action_running = True
    remove_duplicates = False
    while len(CFG.action_queue) > 0:
        print(f"Running Action Queue:\n{[item.name for item in CFG.action_queue]}\n")
        await check_active()
        await async_sleep(0.1)
        try:
            action = CFG.action_queue[0]
        except IndexError:
            log_process("ERROR")
            log(
                "Error! You may have to re-input any commands\nyou requested from the bot."
            )
            sleep(5)
            log("")
            log_process("")
            return
        if CFG.chat_ocr_active:
            for func_name in CFG.chat_block_functions:
                if func_name == action.name:
                    continue

            found_ignore = False
            for func_name in CFG.chat_ignore_functions:
                if func_name == action.name:
                    found_ignore = True
                    break
            if not found_ignore:
                log_process("Deactivating chat A.I")
                await deactivate_ocr()
                log_process("")
        else:
            if (
                action.name not in CFG.chat_block_functions
                or action.name in CFG.chat_ignore_functions
            ):
                CFG.chat_last_non_idle_time = time()

        if action.name == "anti_afk":
            await do_anti_afk()
        elif action.name == "advert":
            await do_advert()
        elif action.name == "autonav":
            await auto_nav(action.values["location"], slow_spawn_detect=False)
            CFG.chat_last_non_idle_time = time()
            log_process("")
            log("")
        elif action.name == "backpack_toggle":
            await click_backpack_button()
            log_process("")
            log("")
        elif action.name == "backpack_item":
            item_number = action.values["item_number"]
            await click_item(item_number)
            log_process("")
            log("")
        elif action.name == "camera_turn":
            turn_direction = action.values["turn_direction"]
            turn_time = action.values["turn_degrees"]
            log_process(f"{turn_time} degrees {turn_direction.upper()}")
            ACFG.look(direction=turn_direction, amount=turn_time)
            log_process("")
        elif action.name == "precision_camera_turn":
            turn_direction = action.values["turn_direction"]
            turn_time = action.values["turn_degrees"]
            log_process(f"{turn_time} degrees {turn_direction.upper()}")
            ACFG.precision_look(direction=turn_direction, amount=turn_time)
            log_process("")
        elif action.name == "camera_pitch":
            pitch_direction = action.values["pitch_direction"]
            pitch_degrees = action.values["pitch_degrees"]
            log_process(f"Tilting {pitch_degrees} degrees {pitch_direction.upper()}")
            ACFG.pitch(amount=pitch_degrees, up=pitch_direction == "up")
            log_process("")
        elif action.name == "camera_zoom":
            zoom_key = action.values["zoom_key"]
            zoom_direction = "in" if zoom_key == "i" else "out"
            zoom_amount = action.values["zoom_amount"]
            log_process(f"Zooming {zoom_direction} {zoom_amount}%")
            ACFG.zoom(zoom_direction_key=zoom_key, amount=zoom_amount)
            log_process("")
        elif action.name == "check_for_better_server":
            crashed = await do_crash_check()
            if not crashed:
                await check_for_better_server()
                await check_active()
            else:
                CFG.action_queue.insert(1, ActionQueueItem("handle_crash"))
        elif action.name == "chat":
            for message in action.values["msgs"]:
                await send_chat(message)
        elif action.name == "chat_with_name":
            name = action.values["name"]
            await send_chat(name)
            await async_sleep(len(name) * CFG.chat_name_sleep_factor)
            for message in action.values["msgs"]:
                await send_chat(message)
        elif action.name == "grief":
            await toggle_collisions()
            ACFG.resetMouse()
            log_process("")
            log("")
        elif action.name == "handle_crash":
            await handle_join_new_server(crash=True)
            remove_duplicates = True
        elif action.name == "handle_join_new_server":
            if await check_active():
                msg = f"[There is a server with >{CFG.player_difference_to_switch} more players!]"
                await send_chat(msg)
                await async_sleep(len(msg) * CFG.chat_name_sleep_factor)
                msg = "[Sorry, I have to switch! Hope to see you there!]"
                await send_chat(msg)
                await async_sleep(len(msg) * CFG.chat_name_sleep_factor)
                await async_sleep(5)
            await handle_join_new_server()
            remove_duplicates = True
        elif action.name == "jump":
            ACFG.jump()
        elif action.name == "leap":
            log_process("Leap Forward")
            time_forward = action.values["forward_time"]
            time_jump = action.values["jump_time"]
            log(f"Moving forward for {time_forward}s and jumping for {time_jump}s")
            await check_active()
            ACFG.leap(forward_time=time_forward, jump_time=time_jump)
            log("")
            log_process("")
        elif action.name == "move":
            log_process("Manual Movement")
            valid_keys = {"w": "Forward", "a": "Left", "s": "Backwards", "d": "Right"}
            move_key = action.values["move_key"].lower()
            if move_key not in valid_keys.keys():
                log(f"Not a valid movement! ({','.join(valid_keys)})")
                await async_sleep(5)
                log("")
                log_process("")
                CFG.action_running = False
                return False
            move_time = action.values["move_time"]
            log(f"Moving {valid_keys[move_key]} for {move_time} FC Units")
            await check_active()
            ACFG.move(direction_key=move_key, amount=move_time)
            log("")
            log_process("")
        elif action.name == "mouse_click":
            await chat_mouse_click()
            log_process("")
            log("")
        elif action.name == "mouse_hide":
            ACFG.resetMouse()
            log_process("")
            log("")
        elif action.name == "mouse_move":
            params = action.values
            had_to_move, area = await move_mouse_chat_cmd(params["x"], params["y"])
            await async_sleep(2)
            if had_to_move:
                try:
                    await params["twitch_ctx"].send(
                        f"[Can't move near '{area}'! Moved mouse to safe range nearby.]"
                    )
                except Exception:
                    print(format_exc())
            log_process("")
            log("")
        elif action.name == "mute":
            await mute_toggle(action.values["set_muted"])
        elif action.name == "rejoin":
            log_process("Rejoining!")
            kill_process(force=True)
            await async_sleep(5)
            log_process("")
            log("")
            await handle_join_new_server()
        elif action.name == "respawn":
            await respawn_character()
            log_process("")
            log("")
        elif action.name == "respawn_force":
            await force_respawn_character()
            log_process("")
            log("")
        elif action.name == "sit":
            await click_sit_button()
        elif action.name == "use":
            log_process("Pressing Use (e)")
            ACFG.use()
            log_process("")
            log("")
        elif action.name == "activate_ocr":
            log_process("Activating Chat A.I.")
            await activate_ocr()
            CFG.chat_ocr_activation_queued = False
            log_process("")
        elif action.name == "ocr_chat":
            CFG.chat_cleared_after_response = False
            await send_chat("[A.I. v2]", ocr=True)
            await async_sleep(0.1)

            for message in action.values["msgs"]:
                await send_chat(message, ocr=True)
            await send_chat("/clear", ocr=True)

            output_log("chat_ai_title", "[Chat AI]")
            output_log("chat_ai_subtitle", "Active")

            CFG.chat_ocr_ready = True
            CFG.chat_cleared_after_response = True
        else:
            print("queue failed")
        CFG.action_queue.pop(0)
        if remove_duplicates:
            original_queue = CFG.action_queue
            for action_queue_item in original_queue:
                if action_queue_item.name == action.name:
                    CFG.action_queue.remove(action_queue_item)
    await async_sleep(0.1)
    CFG.action_running = False


async def add_action_queue(item: ActionQueueItem):
    CFG.action_queue.append(item)
    print("Process Queue")
    await do_process_queue()


async def update_version():
    git_version = check_output(["git", "rev-list", "--count", "HEAD"])  # nosec
    version_string = git_version.decode().split("\n")[0]
    output_log("version", f"v{version_string}")


async def get_updates_log():
    # TODO: Hacky mess, we need something better

    x = get(
        CFG.updates_url, headers={"Cache-Control": "no-cache", "Pragma": "no-cache"}
    )
    if x.status_code != 200:
        output_log("updates_header", "HTTP ERROR")
        output_log("updates_body", f"Could not reach {CFG.updates_url}")
        return

    parsed = document_fromstring(x.text)
    page_data = parsed.get_element_by_id("__NEXT_DATA__").text_content()
    page_data_json = json_loads(page_data)
    page_content = (
        page_data_json.get("props", {})
        .get("pageProps", {})
        .get("staticPageContent", {})
    )
    page_content_json = json_loads(page_content)
    page_content_markdown = page_content_json.get(
        "contentMarkdown", "### ERROR\n ERROR"
    )
    updates = page_content_markdown.replace("   * ", "- ").split("### ")
    if updates[0] == "":
        updates.pop(0)

    latest_update = updates[0].split("\n", 1)

    if len(latest_update) != 2:
        output_log("updates_header", "PARSE ERROR")
        output_log("updates_body", updates[0])
        return
    output_log("updates_header", f"UPDATE LOG ({latest_update[0]})")
    output_log("updates_body", f"{latest_update[1]}\n\n\n")


async def async_main():
    print("[Async_Main] Start")
    output_log("chat_ai_title", "")
    output_log("chat_ai_subtitle", "")
    await update_version()
    await get_updates_log()
    await CFG.add_action_queue(ActionQueueItem("mute", {"set_muted": False}))


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
